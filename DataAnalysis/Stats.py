from DataFrameCollector import DataFrameCollector as DFC
from Database.DBConnect import DbConnection as DB
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

class UsageStats:
    """
    A range of usage statistics in numerical format that can be used for things like reports
    """
    def __init__(self):
        self._collector = DFC()
        self._db = DB()

    """
    These methods were defined so everyone can be lazy and just call the method that suits them. Alternatively, pass
    the dataframe that you have collected yourself elsewhere and pass it to get_frame_stats
    """
    def last_hour_stats(self):
        return self.get_stats('hour', str(datetime.now().replace(microsecond=0) - relativedelta(hours=1)), 1)

    def last_12hour_stats(self):
        return self.get_stats('hour', str(datetime.now().replace(microsecond=0) - relativedelta(hours=12)), 12)

    def last_day_stats(self):
        return self.get_stats('day', str(datetime.now().replace(microsecond=0) - relativedelta(days=1)), 1)

    def last_week_stats(self):
        return self.get_stats('week', str(datetime.now().replace(microsecond=0) - relativedelta(weeks=1)), 1)

    def last_month_stats(self):
        return self.get_stats('month', str(datetime.now().replace(microsecond=0) - relativedelta(months=1)), 1)

    def last_year_stats(self):
        return self.get_stats('year', str(datetime.now().replace(microsecond=0) - relativedelta(years=1)), 1)

    def get_stats(self, period_type, period_start, period_length):
        """
        Get a dictionary of stats for a data frame specified by the following parameters
        :param period_type: hour, day, week, month, year
        :param period_start: the start of the period to collect from
        :param period_length: how long is the period that needs to be collected
        :return: a dictionary containing all the stats for the specified data frame
        """
        stats = {}
        try:
            data_frame = self._collector.collect_period(period_type=period_type, period_start=period_start,
                                                        period_length=period_length)
            stats['average'] = '%.2f' % data_frame.reading.mean()
            stats['max'] = '%.2f' % data_frame.reading.max()
            stats['max_time'] = data_frame.time.max()   # The time at which the maximum occurred
            stats['min'] = '%.2f' % data_frame.reading.min()
            stats['min_time'] = data_frame.time.min()   # The time at which the minimum occurred
            stats['total_usage'] = '%.2f' % data_frame.reading.sum()
            stats['end'] = '%.2f' % data_frame.tail(1).iloc[0]['reading']
            del data_frame  # dispose of the frame right now. We don't need it anymore
            return stats
        except:
            logging.warning('Unable to load data frame')
        return None

    @staticmethod
    def get_frame_stats(data_frame):
        """
        Get a nice dictionary of stats from an existing data frame
        :param data_frame:
        :return:
        """
        stats = {}
        try:
            stats['average'] = '%.2f' % data_frame.reading.mean()
            stats['max'] = '%.2f' % data_frame.reading.max()
            stats['max_time'] = data_frame.time.max()   # The time at which the maximum occurred
            stats['min'] = '%.2f' % data_frame.reading.min()
            stats['min_time'] = data_frame.time.min()   # The time at which the minimum occurred
            stats['total_usage'] = '%.2f' % data_frame.reading.sum()
            stats['end'] = '%.2f' % data_frame.tail(1).iloc[0]['reading']
            del data_frame  # dispose of the frame right now. We don't need it anymore
            return stats
        except:
            logging.warning('Unable to load data frame')
        return None
