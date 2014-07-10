"""
DataCollector: Extract data from the database in specified periods for data analysis

Requires: pandas (http://pandas.pydata.org/)
"""
from Database.DBConnect import DbConnection
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from Database.DBConnect import DbConnection
import logging


class DataFrameCollector():
    """DataCollector."""

    def __init__(self):
        """Stuff that must be initialized when this class is created"""
        self.__start = None
        self.__end = None
        self.__format = '%Y-%m-%d %H:%M:%S'

    def collect_period(self, period_type='hour', period_start=None, period_length=None, period_end=None):
        """Specify the period that you want to collect the data for.
        period_type: hour, day, week, month, year (defaults to hour)
        period_start: When the collection period must start from. Defaults to one period back from current day.
        period_length: How many of the specified periods you want to collect.
        period_end: Alternative to specifying the number of periods. The number of periods will be calculated.

        Example: collect_period(period_type='year', period_start='2011-01-01 00:00:00', period_length=2)
        This will return data for the period 2011-01-01 00:00:00 to 2013-01-01 00:00:00

        Returns a pandas DataFrame object with timestamp and reading columns"""
        if period_start is not None:
            try:
                period_start = datetime.strptime(period_start, '%Y-%m-%d %H:%M:%S')
            except:
                raise ValueError('Invalid date format: date must be in format YYYY-MM-DD HH:MM:SS')
        if period_end is not None:
            try:
                period_end = datetime.strptime(period_end, '%Y-%m-%d %H:%M:%S')
            except:
                raise ValueError('Invalid date format: date must be in format YYYY-MM-DD HH:MM:SS')

        try:
            if period_type == 'hour':
                self.__do_hour(period_start, period_length, period_end)
            elif period_type == 'day':
                self.__do_day(period_start, period_length, period_end)
            elif period_type == 'week':
                self.__do_week(period_start, period_length, period_end)
            elif period_type == 'month':
                self.__do_month(period_start, period_length, period_end)
            elif period_type == 'year':
                self.__do_year(period_start, period_length, period_end)
            else:
                raise Exception  # invalid flag passed
        except:
            raise LookupError('There was an error retrieving your data. Check the values passed to this method.')

        db = DbConnection()
        sql = "select time, reading from powermonitorweb_readings where timestamp >= '%s' and timestamp <= '%s';"
        params = (self.__start.strftime(self.__format), self.__end.strftime(self.__format))
        result = db.execute_query(sql, params)
        db.disconnect()
        if result.rowcount != 0:
            '''Create the DataFrame object from the data collected from the database'''
            data_frame = pd.DataFrame(list(result), columns=('timestamp', 'reading'))
            '''Set the index type to DatetimeIndex to allow us to resample the data'''
            data_frame.set_index(pd.DatetimeIndex(data_frame['timestamp']), inplace=True)
            return data_frame
        else:
            return None

    '''
    It's probably better to try and refactor these methods. They were written like they currently are just to get this
    module working.
    '''

    def __do_hour(self, period_start, period_length, period_end):
        if period_start is None:  # If there is no start period, default to 1 hour back
            period_start = datetime.now() - relativedelta(hours=1)
        self.__start = period_start  # Set the start time for collect_period to get data from

        if period_end is None:
            if period_length is None:  # If no end and period length was set, collect data up to the current time
                period_end = datetime.now()
            else:
                period_end = self.__start + relativedelta(hours=period_length)
        self.__end = period_end  # Set the end time for collect_period to get data from

    def __do_day(self, period_start, period_length, period_end):
        if period_start is None:
            period_start = datetime.now() - relativedelta(days=1)
        self.__start = period_start

        if period_end is None:
            if period_length is None:
                period_end = datetime.now()
            else:
                period_end = self.__start + relativedelta(days=period_length)
        self.__end = period_end

    def __do_week(self, period_start, period_length, period_end):
        if period_start is None:
            period_start = datetime.now() - relativedelta(weeks=1)
        self.__start = period_start

        if period_end is None:
            if period_length is None:
                period_end = datetime.now()
            else:
                period_end = self.__start + relativedelta(weeks=period_length)
        self.__end = period_end

    def __do_month(self, period_start, period_length, period_end):
        if period_start is None:
            period_start = datetime.now() - relativedelta(months=1)
        self.__start = period_start

        if period_end is None:
            if period_length is None:
                period_end = datetime.now()
            else:
                period_end = self.__start + relativedelta(months=period_length)
        self.__end = period_end

    def __do_year(self, period_start, period_length, period_end):
        if period_start is None:
            period_start = datetime.now() - relativedelta(years=1)
        self.__start = period_start

        if period_end is None:
            if period_length is None:
                period_end = datetime.now()
            else:
                period_end = self.__start + relativedelta(years=period_length)
        self.__end = period_end