"""
PowerAlertScraper: Connect to www.poweralert.co.za, and collect data to use for alerts and analysis.
"""
import DataAnalysis.WebScaper
import re


class PowerAlertScraper():
    """Class to scrape power alerts from Eskom's power alert website.
    http://www.poweralert.co.za/poweralert5/index.php"""
    def __init__(self):
        self.__alert = None
        self.__alert_string = None
        self.__usage = None
        self.__usage_string = None
        self.__scraper = DataAnalysis.WebScaper.Scraper()
        self.__scraper.open_page('http://www.poweralert.co.za/poweralert5/index.php')

    def renew_alert_tag(self):
        """Retrieves the tag for the current bar in the electricity usage graph"""
        bs = self.__scraper.get_beautifulsoup()
        self.__alert = bs.find(lambda tag: tag.name == 'img' and tag.has_attr('width') and tag.has_attr('height') and
                                           tag.has_attr('alt') and tag.has_attr('src') and tag['alt'] == "1")
        if self.__alert is not None:  # Remove <> so re doesn't complain
            self.__alert_string = self.__remove_angle_brackets(self.__alert)

    def renew_usage_tag(self):
        """Retrieves the tag for the current electricity usage trend"""
        bs = self.__scraper.get_beautifulsoup()
        self.__usage = bs.find(lambda tag: tag.name == 'img' and tag.has_attr('width') and tag.has_attr('height') and
                                           tag.has_attr('alt') and tag.has_attr('src') and
                                           tag['alt'] == "Electricity usage")
        if self.__usage is not None:  # Remove <> so re doesn't complain
            self.__usage_string = self.__remove_angle_brackets(self.__usage)

    @staticmethod
    def __remove_angle_brackets(tag):
        return str(tag).replace('<', '').replace('>', '')

    def get_alert_level(self):
        """Get the current Eskom power alert/usage level. Usage ranges from 0 to 100."""
        """Still need to figure out what useful information can be extracted from this."""
        pattern = re.compile('(?<=height=")[0-9]?[0-9]')   # Compile regex for the height of the current bar
        match = re.search(pattern, self.__alert_string)    # Find the regex
        return match.group()    # Will only return one item...I hope!

    def get_alert_colour(self):
        """Get the current Eskom alert/usage colour.
        Colours are: green, orange, red, black."""
        pattern = re.compile('(?<=bar_)[a-z]{3,6}')  # Compile regex for the colour of the current alert/usage
        match = re.search(pattern, self.__alert_string)  # Find the regex
        return match.group()    # Again, only one match returned hopefully!

    def get_usage_status(self):
        """Get the current Eskom usage trend. The trends are 'up', 'down', or 'stable'"""
        """Eskom can't decide on consistent name for their colours. Seems like orange and yellow are the same to them.
        Probably shouldn't expect too much from them anyway."""
        pattern = re.compile(
            '((?<=red_)|(?<=green_)|(?<=yellow_)|(?<=black_))[a-z]{2,6}')   # This looks better than the old regex
        match = re.search(pattern, self.__usage_string)
        return match.group()    # And hopefully only one returned here too!