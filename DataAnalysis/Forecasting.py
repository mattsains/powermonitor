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
        # TODO: work out reasonable values for time intervals
        # for now I am just going to include 1hr from the actual data, and predict 1hr of usage
        end = to_datetime(datetime_as_string(resampled_frame.index.values[len(resampled_frame)-1]))  # end of frame
        start_pred = str(end - relativedelta(hours=1))
        end_pred = str(end + relativedelta(hours=1))
        pred = result.predict(start=start_pred, end=end_pred)
        return pred

    def predict_usage(self, data_frame, ptype='hour', smooth=False):
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
