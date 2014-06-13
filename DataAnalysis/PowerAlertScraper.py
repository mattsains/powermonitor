"""
PowerAlertScraper: Connect to www.poweralert.co.za, and collect data to use for alerts and analysis.
"""
import DataAnalysis.WebScraper
import re


class PowerAlertScraper():
    """Class to scrape power alerts from Eskom's power alert website.
    http://www.poweralert.co.za/poweralert5/index.php"""
    def __init__(self):
        self.__alert = None
        self.__alert_string = None
        self.__usage = None
        self.__usage_string = None
        self.__scraper = DataAnalysis.WebScraper.Scraper()
        self.__scraper.open_page('http://www.poweralert.co.za/poweralert5/index.php')

    def renew_tags(self):
        """
        Renew the alert tag and usage tags at the same time to reduce network usage
        """
        bs = self.__scraper.get_beautifulsoup()
        for td in bs.find_all('td', {'bgcolor': '#FEC5D5', 'align': 'center'}):
            for img in td.find_all('img'):
                self.__alert = img  # A for loop had to be used because td.find_all is an iterable
        if self.__alert is not None:  # Remove <> so re doesn't complain
            self.__alert_string = self.__remove_angle_brackets(self.__alert)

        for img in bs.find_all('img', {'alt': 'Electricity usage'}):
            self.__usage = img  # A for loop had to be used because img.find_all is an iterable
        if self.__usage is not None:  # Remove <> so re doesn't complain
            self.__usage_string = self.__remove_angle_brackets(self.__usage)

    @staticmethod
    def __remove_angle_brackets(tag):
        return str(tag).replace('<', '').replace('>', '')

    def get_alert_level(self):
        """Get the current Eskom power alert/usage level. Usage ranges from 0 to 100."""
        """Still need to figure out what useful information can be extracted from this."""
        pattern = re.compile('(?<=height=")[0-9]?[0-9]')   # Compile regex for the height of the current bar
        if self.__alert_string is not None:
            match = re.search(pattern, self.__alert_string)    # Find the regex
            return match.end()   # Will only return one item...I hope!
        else:
            return None

    def get_alert_colour(self):
        """Get the current Eskom alert/usage colour.
        Colours are: green, orange, red, black."""
        pattern = re.compile('(?<=bar_)[a-z]{3,6}')  # Compile regex for the colour of the current alert/usage
        if self.__alert_string is not None:
            match = re.search(pattern, self.__alert_string)  # Find the regex
            return match.group()    # Again, only one match returned hopefully!
        else:
            return None

    def get_usage_status(self):
        """Get the current Eskom usage trend. The trends are 'up', 'down', or 'stable'"""
        """Eskom can't decide on consistent name for their colours. Seems like orange and yellow are the same to them.
        Probably shouldn't expect too much from them anyway."""
        pattern = re.compile(
            '((?<=red_)|(?<=green_)|(?<=yellow_)|(?<=black_))[a-z]{2,6}')   # This looks better than the old regex
        if self.__usage_string is not None:
            match = re.search(pattern, self.__usage_string)
            return match.group()    # And hopefully only one returned here too!
        else:
            return None