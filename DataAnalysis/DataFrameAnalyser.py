import pandas as pd
import statsmodels as sm


class DataFrameAnalyser():
    """Analyse the data collected in the DataFrame"""
    def __init__(self):
        """Initialize any class variables or methods"""

    def downsample_frame(self, data_frame, rate='5min'):
        """Down-sample the frame to specified period"""
        if data_frame is pd.DataFrame:
            data_frame.resample(rate, how='mean', closed='right')
        pass