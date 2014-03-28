import DataAnalysis.WebScaper

class PowerAlertScraper():
    """Class to scrape power alerts from Eskom's power alert website.
    http://www.poweralert.co.za/poweralert5/index.php"""
    def __init__(self):
        self.__alert = None
        self.__usage = None
        self.__scraper = DataAnalysis.WebScaper.Scraper()
        self.__scraper.open_page('http://www.poweralert.co.za/poweralert5/index.php')

    def renew_alert_tag(self):
        """Retrieves the tag for the current bar in the electricity usage graph"""
        bs = self.__scraper.get_beautifulsoup()
        self.__alert = bs.find(lambda tag: tag.name == 'img' and tag.has_attr('width') and tag.has_attr('height') and
                                           tag.has_attr('alt') and tag.has_attr('src') and tag['alt'] == "1")

    def renew_usage_tag(self):
        """Retrieves the tag for the current eletricity usage trend"""
        bs = self.__scraper.get_beautifulsoup()
        self.__usage = bs.find(lambda tag: tag.name == 'img' and tag.has_attr('width') and tag.has_attr('height') and
                                           tag.has_attr('alt') and tag.has_attr('src') and
                                           tag['alt'] == "Electricity usage")

    def get_alert_level(self):
        #TODO: code this
        return None

    def get_alert_color(self):
        #TODO: code this
        return None

    def get_alert_status(self):
        #TODO: code this
        return None