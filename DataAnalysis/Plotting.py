from statsmodels.discrete.discrete_model import L1BinaryResults

__author__ = 'Vincent'
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO


class Plotter():
    """Plotter"""

    def __init__(self):
        """Stuff that must be initialized when this class is created"""

    def ewmaResampling(self, dataFrameIn, weight=1, freqVal='1min', minPeriodsVal=10):
        """Specify the dataFrame that you want to plot
        :rtype : object
        freqVal: "1min","1H", "1M", "1S" or any multiples thereof
        weight: This is how much does the observation affect the exponentially weighted mean
        minPeriodsVal: This is the number of values you need in order for this plot to be useful

        NOTE:
        This emwa is a form a resampling.
        It places more weight on recent observations
        The 1 minute frequency is the accepted min for frequency, even though if this is done over a few weeks
        would possibly want freq to be a few hours, will refactor for that case. This is v1.0

        Return: This will return a dataFrame resampled under the Exponential weight moving average principal
        """
        if (dataFrameIn == None):
            raise ValueError("Invalid dataFrame, pass a DataFrame with actual data")
        if (weight <= 0):
            raise ValueError("The weight is invalid, should be a float > 0")
        if (minPeriodsVal <= 0):
            raise ValueError("The min number of periods is invalid, should be a float >0")

        # review comments: don't replace a potentially meaningful exception with one that only guesses what the problem is
        result = pd.ewma(dataFrameIn.reading, weight, freqVal, minPeriodsVal)
        return result

    def plotDataBetweenTwoDataFrames(self, dataFrameOriginal, dataFrameWeighted, YLabel, legendLabelOriginal="",
                                     legendLabelWeighted="", title="", XLabel="",
                                     fileName=None):
        """Specify the dataFrame that you want to plot, a weighted vs actual readings currently
        Title: A string title for the plot
        XLabel: The label for the x axis : Time Stamp
        YLabel: The label for the y axis : reading(kWh)
        fileName: file name you want to save as

        Return: return the figure or a stringIO of the figure if no filename is given
        """
        # Review comments: How does this end up in the plt object? Don't have docs to check
        dataFrameOriginal.reading.plot(label=legendLabelOriginal, color='g')
        dataFrameWeighted.plot(label=legendLabelWeighted, color='Y', marker='o')

        if (title):
            plt.title(title)
        if (YLabel):
            plt.ylabel(YLabel)
        if (XLabel):
            plt.xlabel(XLabel)

        if (legendLabelOriginal or legendLabelWeighted):
            plt.legend()

        if (fileName is None):
            buffer = StringIO()
            plt.savefig(buffer)
            return buffer.getvalue()
        else:
            fileNameSplit = fileName.split(".")
            if ((fileNameSplit[-1] == "svg") or (fileNameSplit[-1] == "png") or (fileNameSplit[-1] == "jpg") ):
                return plt.savefig(fileName)
            else:
                return None

    def turnDataFrameIntoGraph(self, dataFrameIn, weight=1, freqVal='1min', minPeriodsVal=10,
                               title="", YLabel="", XLabel="", fileName=None, weightType="EWMA"):
        """Specify the dataFrame that you want to plotted against its EMWA
        you require the parameters to shape the plot.
        The parameters are explained in the self.expoweightedresampling and self.plotDataBetweenTwodataFrames
        fileName: This will be what you want to save the file as < not sure if I should keep this
        or hard code the fileName to keep consistency
        Return: This will attempt to return the file that stores the figure for the plot
        """
        dataFrameWeighted = None
        # # check length of typeWeight
        if (weightType == "EWMA"):
            dataFrameWeighted = self.ewmaResampling(dataFrameIn, weight, freqVal, minPeriodsVal)
            legendToSend = "Weighted Average plot"
        else:
            dataFrameWeighted = self.equalWeightMovingAverage(dataFrameIn, freqVal, minPeriodsVal)
            legendToSend = "Rolling Average plot"

        return self.plotDataBetweenTwoDataFrames(dataFrameIn, dataFrameWeighted, legendLabelWeighted=legendToSend,
                                                 title=title, YLabel=YLabel, XLabel=XLabel, fileName=fileName)

    def equalWeightMovingAverage(self, dataFrameIn, freqVal='1min', minPeriodsVal=10):
        """ Resamples data using a rolling mean
        :rtype : object
        freqVal: "1min","1H", "1M", "1S" or any multiples there of
        min_periodsVal: This is the number of values you need in order for this plot to be useful
        NOTE:
        The 1 minute frequency is the accepted min for frequency, even though if this is done over a few weeks
        would possibly want freq to be a few hours, will refactor for that case. This is v1.0

        Return: This will return a dataFrame resampled under the equal weight moving average principal
        """

        if (dataFrameIn is None):
            raise ValueError('Invalid dataFrame, Please pass dataFrame with actual data')
        if (minPeriodsVal < 1):
            raise ValueError("The min number of periods is invalid")
        # Review comments: same as before
        result = pd.rolling_mean(dataFrameIn.reading, minPeriodsVal, freqVal)
        return result

    def singlePlotOfFrame(self, dataFrameIn, title="", legendLabel="", YLabel="", XLabel="",
                          fileName=None):
        """Specify the dataFrame that you want to plot, single dataFrame
        Title: The string title for the plot
        YLabel: The label for the y axis
        XLabel: The label for the x axis
        fileName: file name you want to save as or None for a stringIO

        Return: return the figure or a stringIO of the figure
        """
        # Review comments: How does this end up in the plt object? Don't have docs to check
        dataFrameIn.reading.plot(label=legendLabel, color='g')

        if (title):
            plt.title(title)
        if (YLabel):
            plt.ylabel(YLabel)
        if (XLabel):
            plt.xlabel(XLabel)

        if (legendLabel):
            plt.legend()

        if (fileName is None):
            buffer = StringIO()
            plt.savefig(buffer)
            return buffer.getvalue()
        else:
            fileNameSplit = fileName.split(".")
            if ((fileNameSplit[-1] == "svg") or (fileNameSplit[-1] == "png") or (fileNameSplit[-1] == "jpg") ):
                return plt.savefig(fileName)
            else:
                return None