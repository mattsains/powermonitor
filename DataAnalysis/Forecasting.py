from numpy import zeros, ndarray, datetime_as_string
from pandas import ewma, DataFrame, Series, to_datetime
from statsmodels.api import tsa
from dateutil.relativedelta import relativedelta


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
        # Currently the forecast requires 12 hours of readings with no NaN or inf values
        # So far it seems reasonably accurate to predict the usage for the next hour, but we can play with this
        end = to_datetime(datetime_as_string(resampled_frame.index.values[len(resampled_frame)-1]))  # end of frame
        start_pred = str(end - relativedelta(hours=12))  # we can play around with this number a bit
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
            return self._ar_prediction(data_frame, '5T')
        else:
            return ewma(self._ar_prediction(data_frame.reading, '5T'), com=2)
