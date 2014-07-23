# Any bound classes that cannot be instantiated using the scheduler should be called from this script
from DataAnalysis.PowerAlertScraper import PowerAlertScraper as PAS

def power_alert_scraper__renew_tags():
    scraper = PAS()
    scraper.renew_tags()