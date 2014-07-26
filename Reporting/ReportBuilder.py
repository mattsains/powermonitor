"""
ReportBuilder: Compile a report/alert to be emailed to the user into an HTML formatted message.

Requires: 
"""
from Reporting.Mailer import Mailer
import DataAnalysis.PowerAlertScraper
from DataAnalysis.Plotting import Plotter
from DataAnalysis.Stats import UsageStats
from DataAnalysis.DataFrameCollector import DataFrameCollector
from powermonitorweb.models import AlertTip, User
from django.core.urlresolvers import reverse
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportBuilder():
    """ReportBuilder"""

    def __init__(self):
        """Stuff to be initialized with class"""
        self._alert_scraper = DataAnalysis.PowerAlertScraper.PowerAlertScraper()
        self._mailer = Mailer()
        self._plotter = Plotter()
        self._usage_stats = UsageStats()
        self._collector = DataFrameCollector()

    def build_power_alert_report(self, power_alert_status):
        """Send an Eskom power alert to a user"""
        # needs: title name power_alert_status power_peak reporting_url image_url tips[]
        frame = self._collector.collect_period(period_type='hour',
                                               period_start=str(datetime.now() - relativedelta(hours=1)),
                                               period_length=1)
        stats = self._usage_stats.get_frame_stats(frame)
        self._plotter.plot_single_frame(data_frame=frame, title='Usage for last hour', y_label='Usage (kW',
                                        x_label='Time', file_name='last_hour.svg')

        email_context = {}
        images = []

        email_context['power_alert_status'] = power_alert_status
        if email_context['power_alert_status'] == 'critical' or 'warning':
            email_context['title'] = "Power Alert Status %s" % email_context[
                'power_alert_status'].capitalize()
        else:
            return  # I don't think it's necessary to send "power's all fine chaps!"


        email_context['power_peak'] = stats['max']
        email_context['power_peak_time'] = stats['max_time']
        # I'm guessing this is where it was intended to link to
        email_context['reporting_url'] = reverse('powermonitorweb:graphs')

        email_context['image_url'] = 'cid:graph'
        email_context['tips'] = AlertTip.objects.filter(
            Alert='0')  # TODO: Still need to work out how to query the reporting tips
        images.append('last_hour.svg')

        # build a report for each user
        for user in User.objects.all():
            if user.username != 'powermonitor':  # we don't want to email the sysadmin
                try:
                    email_context['name'] = user.first_name

                    # Add email to the mail list. All mails will be sent once all reports have been built
                    self._mailer.create_multipart_mail(template_name='PowerAlert', email_context=email_context,
                                                       subject=email_context['title'], recipients=[user.email,],
                                                       images=tuple(images))
                except:
                    pass
        self._mailer.send_emails(self._mailer.get_mail_list())  # send all the emails at once

    def send_usage_report(self, user, report_start, report_end):
        """Send a report of electricity consumption"""
        # needs: title name report_period report_begin report_end power_sum power_average image_url reporting_url

    def send_usage_alert(self, user, alert_event):  # TODO evaluate parameter choice here
        """Send an alert of electricity consumption"""
        # needs: title name power_peak power_average image_url reporting_url