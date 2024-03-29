from DataFrameCollector import DataFrameCollector as DFC
from Database.DBConnect import DbConnection as DB
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
import Plotting as plt
import pandas as pd
from numpy import float64
import Resampling as rs
from numpy import zeros, ndarray, datetime_as_string
from pandas import ewma, DataFrame, Series, to_datetime
from statsmodels.api import tsa
from dateutil.relativedelta import relativedelta

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
        return self.get_stats('hour', datetime.utcnow().replace(microsecond=0) - relativedelta(hours=1), 1)

    def last_12hour_stats(self):
        return self.get_stats('hour', datetime.utcnow().replace(microsecond=0) - relativedelta(hours=12), 12)

    def last_day_stats(self):
        return self.get_stats('day', datetime.utcnow().replace(microsecond=0) - relativedelta(days=1), 1)

    def last_week_stats(self):
        return self.get_stats('week', datetime.utcnow().replace(microsecond=0) - relativedelta(weeks=1), 1)

    def last_month_stats(self):
        return self.get_stats('month', datetime.utcnow().replace(microsecond=0) - relativedelta(months=1), 1)

    def last_year_stats(self):
        return self.get_stats('year', datetime.utcnow().replace(microsecond=0) - relativedelta(years=1), 1)

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

    def get_frame_stats(self, data_frame):
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
            stats['total_per_hour'] = '%.2f' % data_frame.reading.mean()
            stats['end'] = '%.2f' % data_frame.tail(1).iloc[0]['reading']
            del data_frame  # dispose of the frame right now. We don't need it anymore
            return stats
        except:
            logging.warning('Unable to load data frame')
        return None

    def get_total_savings(self,data_frame):
        """
        data_frame: The frame of data you want savings for!!

        :param data_frame:
        :return: The total amount of savings
        """
        if data_frame is None:
            raise ValueError("Invalid dataFrame, pass a DataFrame with actual data")
        if (len(data_frame)<=1):
            raise ValueError("The passed data frame doesn't have enough data to generate savings")
        timeStart = (data_frame.ix[len(data_frame)-2].name)
        timeNext = (data_frame.ix[len(data_frame)-1].name)

        timeDiff = timeNext - timeStart
        timeDiffSeconds = timeDiff.seconds
        freq = ""
        value = 0

        if ((timeDiffSeconds//60) >= 1):
            freq = "min"
            value = timeDiffSeconds//60
        elif ((timeDiffSeconds//60) == 0):
            freq = "s"
            value = timeDiffSeconds
        elif ((timeDiffSeconds//(3600)) >= 1):
            freq = "h"
            value = timeDiffSeconds//3600

        freq = str(value) + freq

        data_frame_weighted = plt.Plotter().ewma_resampling(data_frame,freq)
        data_frame_weighted = pd.DataFrame(data_frame_weighted,columns=("reading",))
        totalSavings = float64(0)
        diff_frame = data_frame.subtract(data_frame_weighted)
        return diff_frame.reading.sum(axis=0)


class PowerForecasting:
    """
    Input a Pandas DataFrame with actual readings, and return a Pandas DataFrame with power forecasts
    """
    def _ar_prediction(self, data_frame, freq):
        """
        Generate a prediction using an Autoregressive Model
        :return: A dataframe with predicted usage
        """
        resampled_frame = data_frame.resample(freq, how='mean', closed='right')
        model = tsa.AR(resampled_frame, freq=freq)
        result = model.fit(maxlag=5, method='mle', transparams=True, disp=-1)
        # Currently the forecast requires 6 hours of readings with no NaN or inf values
        # So far it seems reasonably accurate to predict the usage for the next hour, but we can play with this
        end = to_datetime(datetime_as_string(resampled_frame.index.values[len(resampled_frame)-1]))  # end of frame
        start_pred = str(end - relativedelta(hours=5))  # we can play around with this number a bit
        end_pred = str(end + relativedelta(hours=1))  # you can try increasing this if you want to
        return result.predict(start=start_pred, end=end_pred)

    def predict_usage(self, data_frame, smooth=False):
        """
        Predict usage based on data in the given DataFrame.
        At the moment no other values will be taken in. Everything will be calculated from here.
        :param resampled_data_frame: Pandas DataFrame
        :param ptype: period type for prediction. currently only 'hour'
        :param smooth: return a frame with smoothed data using EWMA if True.
        :return: Pandas DataFrame containing predicted values
        """
        if not smooth:
            prediction_frame = self._ar_prediction(data_frame, '5T')
            return prediction_frame[int(len(prediction_frame)/1.5):]  # silly! you can't slice a frame with a fraction
        else:
            prediction_frame = ewma(self._ar_prediction(data_frame.reading, '5T'), com=2)
            return prediction_frame[int(len(prediction_frame)/1.5):]
