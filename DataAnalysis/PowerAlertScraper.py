"""
PowerAlertScraper: Connect to www.poweralert.co.za, and collect data to use for alerts and analysis.
"""
import DataAnalysis.WebScraper
import re
from Decorators import Singleton
# from Reporting.ReportBuilder import ReportBuilder # TODO: Fix issues in ReportBuilder


@Singleton
class PowerAlertScraper:
    """Class to scrape power alerts from Eskom's power alert website.
    http://www.poweralert.co.za/poweralert5/index.php"""
    def __init__(self):
        self.__alert = None
        self.__alert_string = None
        self.__usage = None
        self.__usage_string = None
        self.__scraper = DataAnalysis.WebScraper.Scraper()
        self.__scraper.open_page('http://www.poweralert.co.za/poweralert5/index.php')
        self.__current_readings = {'level': 0, 'colour': 'green', 'status': 'down'}

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

    def check_for_change(self):
        """
        Check to see if there has been a change in any of the values
        :return: Dictionary containing the changed state of the level, colour, and status from poweralert
        """
        self.renew_tags()   # renew the tags to check if there was any change
        poweralert = {'level': False, 'colour': False, 'status': False}
        # Check if there was a change in the power level
        if self.get_alert_level() != self.__current_readings['level']:
            poweralert['level'] = True
            self.__current_readings['level'] = self.get_alert_level()
        # Check if there was a change in the colour (green, yellow/orange, red, black)
        if self.get_alert_colour() != self.__current_readings['colour']:
            poweralert['colour'] = True
            self.__current_readings['colour'] = self.get_alert_colour()
        # Check if there was a change in the current status (up, down, or stable)
        if self.get_usage_status() != self.__current_readings['status']:
            poweralert['status'] = True
            self.__current_readings['status'] = self.get_usage_status()
        # yield the status of each of the values (True for change, False for no change)
        return poweralert

    @staticmethod
    def __remove_angle_brackets(tag):
        """
        remove the html angle brackets from the tag to ready it for regex search
        :param tag: The tag to be stripped
        :return: html tag sans angle brackets (str)
        """
        return str(tag).replace('<', '').replace('>', '')

    def get_alert_level(self):
        """
        Get the current Eskom power alert/usage level. Usage ranges from 0 to 100.
        :return: alert level (int)
        """
        """Still need to figure out what useful information can be extracted from this."""
        pattern = re.compile('(?<=height=")[0-9]?[0-9]')   # Compile regex for the height of the current bar
        if self.__alert_string is not None:
            match = re.search(pattern, self.__alert_string)    # Find the regex
            return int(match.end())   # Will only return one item...I hope!
        else:
            return None

    def get_alert_colour(self):
        """
        Get the current Eskom alert/usage colour.
        Colours are: green, orange, red, black.
        :return: alert colour (str)
        """
        pattern = re.compile('(?<=bar_)[a-z]{3,6}')  # Compile regex for the colour of the current alert/usage
        if self.__alert_string is not None:
            match = re.search(pattern, self.__alert_string)  # Find the regex
            return match.group()    # Again, only one match returned hopefully!
        else:
            return None

    def get_usage_status(self):
        """
        Get the current Eskom usage trend. The trends are 'up', 'down', or 'stable'
        :return: usage status (str)
        """
        """Eskom can't decide on consistent name for their colours. Seems like orange and yellow are the same to them.
        Probably shouldn't expect too much from them anyway."""
        pattern = re.compile(
            '((?<=red_)|(?<=green_)|(?<=yellow_)|(?<=black_))[a-z]{2,6}')   # This looks better than the old regex
        if self.__usage_string is not None:
            match = re.search(pattern, self.__usage_string)
            return match.group()    # And hopefully only one returned here too!
        else:
            return None

    def check_alert_status(self):
        """
        Get the status of the national power grid
        :return: 'critical', 'warning', or 'stable'
        """
        # TODO: This possibly needs a bit more thought. Are there other criteria we should use?
        stats = self.check_for_change()
        # builder = ReportBuilder()
        if stats['colour'] and stats['status']:  # if both of these are True
            if self.get_alert_colour() == 'red' and self.get_usage_status() == 'up':
                # builder.build_power_alert_report(power_alert_status='warning')
                return 'warning'
            elif self.get_alert_colour() == 'black' and self.get_usage_status() == 'up':
                # builder.build_power_alert_report(power_alert_status='critical')
                return 'critical'
            else:   # TODO: Should the user be notified if the colour is red but usage is down?
                return 'stable'
        else:
            return 'stable'