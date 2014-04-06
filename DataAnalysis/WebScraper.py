"""
WebScaper: searches websites for items matching regular expressions

Requires: beautifulsoup4 (http://www.crummy.com/software/BeautifulSoup/bs4/doc/)
"""
from bs4 import BeautifulSoup
import urllib
import urllib.request
import logging
import re


class Scraper():
    """Class to scape websites for data"""
    def __init__(self):
        self.__url = None
        self.__soup = None

    def open_page(self, page_url):
        """Connect to 'url' and extract html content"""
        try:
            self.__url = urllib.request.urlopen(page_url)
            self.__soup = BeautifulSoup(self.__url.read())
        except (urllib.URLError, urllib.HTMLParserError):
            logging.warning("Could not parse: " + page_url)

    def find_expression(self, regex):
        """Find the content matching the regular expression 'regex' in the html content of the page
        and returns the matches. Returns None if nothing is found."""
        pattern = re.compile(regex)
        url_string = self.__url.read().decode(encoding='UTF-8')
        match = re.search(pattern, url_string)
        if len(match) == 0:
            return None
        else:
            return match

    def get_beautifulsoup(self):
        """Return the BeautifulSoup object for the page to do manual tag searching."""
        return self.__soup