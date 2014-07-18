from numpy import zeros, ndarray, datetime_as_string
from pandas import ewma, DataFrame, Series, to_datetime


class PowerForecasting:
    """
    Input a Pandas DataFrame with actual readings, and return a Pandas DataFrame with power forecasts
    """

    @staticmethod
    def _predict(data_frame, span, periods, freq, adjust=False):
        """
        Given a Pandas DataFrame, use exponentially weighted moving average to predict future values
        :param data_frame: input frame
        :param span: an integer between 1 and len(data_frame). how far back to we want to weight
        :param periods: the number of periods to predict. each period is the same length as the period length of the
                        dataframe
        :param freq: Frequency required for ewma
        :param adjust: Divide by decaying adjustment factor in beginning periods to account for imbalance in relative
                       weightings (see Pandas documentation)
        :return: A list of predicted values
        """
        if data_frame is None:
            raise ValueError('data_frame cannot be None')
        if not span or span < 0 or span > len(data_frame):
            raise ValueError('span must have a value and must be between 1 and len(data_frame)')
        if not periods:
            raise ValueError('periods cannot be None')
        if type(data_frame) is not Series:
            print type(data_frame)
            raise TypeError('data_frame must be type DataFrame')
        if type(span) is not int:
            raise TypeError('span must be an integer')
        if type(periods) is not int:
            raise TypeError('periods must be an integer')
        predict_x = zeros((span+periods,))
        predict_x[:span] = data_frame[-span:]
        prediction = ewma(predict_x, span=span, freq=freq, adjust=adjust)[span:]
        return prediction

    def _add_timestamps_to_predicted_values(self, resampled_frame, predicted_values):
        """
        adds timestamps to the predicted values
        :param resampled_frame: the DataFrame that the predicted values were calculated from
        :param predicted_values: the predicted values that need timestamps
        :return: a Pandas DataFrame containing predicted values with associated timestamps
        """
        if resampled_frame is None:
            raise ValueError('resampled_frame must have value')
        if type(resampled_frame) is not DataFrame:
            raise TypeError('resampled_frame must be a Pandas DataFrame')
        if predicted_values is None:
            raise ValueError('predicted_values must have a value')
        if type(predicted_values) is not ndarray:
            print type(predicted_values)
            raise TypeError('predicted_values must be a list')

        start = to_datetime(datetime_as_string(resampled_frame.index.values[0]))  # time at start of frame
        end = to_datetime(datetime_as_string(resampled_frame.index.values[len(resampled_frame)-1])) # end of frame

        time_diff = end - start     # time difference between start and end of frame
        period = time_diff / len(predicted_values)  # length of a single period
        predicted_start = end + period  # start time of predicted values
        pred_list = []
        for val in predicted_values:
            pred_list.append((predicted_start, val))
            predicted_start += period
        return DataFrame(pred_list, columns=('time', 'predicted_reading'))

    def predict_usage(self, data_frame, ptype='hour'):
        """
        Predict usage based on data in the given DataFrame.
        At the moment no other values will be taken in. Everything will be calculated from here.
        :param resampled_data_frame: Pandas DataFrame
        :param ptype: period type for prediction. currently only 'hour'
        :return: Pandas DataFrame containing predicted values
        """
        resampled_frame = data_frame.resample('5T', how='mean', closed='right')
        span = len(resampled_frame) - 1
        predicted_values = self._predict(data_frame=data_frame.reading, span=span, periods=12, freq='5T', adjust=False)
        return self._add_timestamps_to_predicted_values(resampled_frame, predicted_values)
