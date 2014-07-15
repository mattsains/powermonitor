"""
ReportBuilder: Compile a report/alert to be emailed to the user into an HTML formatted message.

Requires: 
"""
from Reporting.Mailer import Mailer
import DataAnalysis.PowerAlertScraper
from DataAnalysis.Plotting import Plotter
from powermonitorweb.models import AlertTip, User
from django.core.urlresolvers import reverse


class ReportBuilder():
    """ReportBuilder"""

    def __init__(self):
        """Stuff to be initialized with class"""
        self._alert_scraper = DataAnalysis.PowerAlertScraper.PowerAlertScraper()
        self._mailer = Mailer()
        self._plotter = Plotter()

    def build_power_alert_report(self, user, power_alert_status):
        """Send an Eskom power alert to a user"""
        # needs: title name power_alert_status power_peak reporting_url image_url tips[]
        for user in User.objects.all():
            if user.username != 'powermonitor':  # we don't want to email the sysadmin
                try:
                    email_context = {}

                    email_context['power_alert_status'] = power_alert_status
                    if email_context['power_alert_status'] == 'critical' or 'warning':
                        email_context['title'] = "Power Alert Status %s" % email_context[
                            'power_alert_status'].capitalize()
                    else:
                        return  # I don't think it's necessary to send "power's all fine chaps!"

                    email_context['power_peak'] = '123'  #Stats.GetMaxLastHour()  # TODO
                    email_context['reporting_url'] = reverse('powermonitorweb.report.main')  # TODO

                    email_context['image_url'] = 'cid:graph'
                    email_context['name'] = user.first_name
                    email_context['tips'] = AlertTip.objects.filter(
                        Alert='0')  # TODO: I dunno guys I'm so disconnected from this project :(
                    image = self._plotter.plotLastHourOrSomething()  # TODO graph image filename goes here

                    # Add email to the mail list. All mails will be sent once all reports have been built
                    self._mailer.create_multipart_mail('PowerAlert', email_context, email_context['title'], user.email,
                                                               images=(('graph', 'graphs/' + image),))
                except:
                    pass  # I'm not hell-bent on sending power alerts. They're stupid anyway
        self._mailer.send_emails(self._mailer.get_mail_list())  # send all the emails at once

    def send_usage_report(self, user, report_start, report_end):
        """Send a report of electricity consumption"""
        # needs: title name report_period report_begin report_end power_sum power_average image_url reporting_url

    def send_usage_alert(self, user, alert_event):  # TODO evaluate parameter choice here
        """Send an alert of electricity consumption"""
        # needs: title name power_peak power_average image_url reporting_url