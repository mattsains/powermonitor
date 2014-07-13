"""
ReportBuilder: Compile a report/alert to be emailed to the user into an HTML formatted message.

Requires: 
"""
from Reporting.Mailer import Mailer
import DataAnalysis.PowerAlertScraper
import DataAnalysis.Plotting

class ReportBuilder():
    """ReportBuilder"""
    def __init__(self):
        """Stuff to be initialized with class"""
        self._alert_scraper=DataAnalysis.PowerAlertScraper.PowerAlertScraper()
        self._mailer=Mailer.Mailer()
        self._plotter=Plotting.Plotter()
        
    def send_power_alert(self, user):
        """Send an Eskom power alert to a user"""
        # needs: title name power_alert_status power_peak reporting_url image_url tips[] 
        try:
            email_context={}
            
            email_context['power_alert_status'] = self._alert_scraper.getAlertStatus() #TODO
            if email_context['power_alert_status'] == 'critical' #TODO: make sure these are right
                email_context['title'] = "Power Alert Status Critical"
            elif email_context['power_alert_status'] == 'warning'
                email_context['title'] = "Power Alert Status Warning"
            else
                return # I don't think it's necessary to send "power's all fine chaps!"
            
            email_context['power_peak'] = Stats.GetMaxLastHour() #TODO
            email_context['reporting_url'] = reverse('powermonitorweb.report.main') #TODO
            
            email_context['image_url'] = 'cid:graph'
            email_context['name'] = user.first_name
            email_context['tips'] = AlertTips.objects.filter(Alert='0') #TODO: I dunno guys I'm so disconnected from this project :(
            image = self._plotter.plotLastHourOrSomething() #TODO graph image filename goes here
            
            email=self._mailer.create_multipart_mail('PowerAlert', email_context, email_context['title'], recipients, images={'graph': })
            self._mailer.send_emails([email,])
        except:
            pass #I'm not hell-bent on sending power alerts. They're stupid anyway
    
    def send_usage_report(self, user, report_start, report_end):
        """Send a report of electricity consumption"""
        # needs: title name report_period report_begin report_end power_sum power_average image_url reporting_url
    
    def send_usage_alert(self, user, alert_event): #TODO evaluate parameter choice here
        """Send an alert of electricity consumption"""
        # needs: title name power_peak power_average image_url reporting_url