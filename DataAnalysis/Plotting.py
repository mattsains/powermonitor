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

    def expoweightedresampling(self,dateFrameIn,amountOfWeight = 1,freqVal='1min',min_periodsVal=10):
        """Specify the dateFrame that you want to plot
        :rtype : object
        freqVal: "1min","1H", "1M", "1S" or any multiples there of
        amountOfWeight: This is how much does the observation affect the exponentially weighted mean
        min_periodsVal: This is the number of values you need in order for this plot to be useful

        NOTE:
        This emwa is a form a resampling, so you could actually use this to resample data.
        The great thing is that it places extra weight on observations with a recent time stamp
        The 1 minute frequency is the accepted min for frequency, even though if this is done over a few weeks
        would possibly want freq to be a few hours, will refactor for that case. This is v1.0

        Return: This will return a dateFrame resampled under the Exponential weight moving average principal
        """
        if (dateFrameIn == None):
            raise ValueError('Invalid DateFrame, Please pass DateFrame with actually data')
        if (amountOfWeight<= 0):
            raise ValueError("The amount of weight is incorrect, should be a float > 0")
        if (min_periodsVal<= 0):
            raise ValueError("The min number of periods isn't valid")
        toReturn = None
        try:
            toReturn = pd.ewma(dateFrameIn.reading,amountOfWeight,freqVal,min_periodsVal)
        except:
            raise ValueError("The frequency %d isn't valid for Pandas",freqVal)
        return toReturn

        # still need to decide if maybe i should refactor this into two functions
        # one that returns the fig as a file from the plot
        # one that down samples the data using EWMA

    def plotDataBetweenTwoDateFrames(self,dateFrameOriginal,dateFrameWeighted,LegendLabelOriginal="Current reading",
                                     LegendLabelWeighted="weighted plot",Title="YourTitle",YLabel="Y",XLabel="X",
                                     fileName="plotted.svg"):
        """Specify the dateFrame that you want to plot, a weighted vs actual readings currently
        Title: The title for the plot : "THE BEST PLOT EVER"
        YLabel: The label for the y axis : reading(kWh)
        XLabel: The label for the x axis : Time Stamp
        fileName: file name you want to save as

        Return: return the figure or a stringIO of the figure
        """
        FileToReturn = None
        canSave = False
        splitted = fileName.split(".")
        buffer = StringIO()
        if (len(LegendLabelOriginal) <= 0):
                LegendLabelOriginal="current readings"
        if (len(LegendLabelWeighted) <= 0):
                LegendLabelWeighted="weighted readings"

        if ((splitted[1] == "svg") or (splitted[1] == "png") or (splitted[1] == "jpg") ):
            canSave = True # will add more
            #fig = plt.figure() # not needed # the below needs to still be tested, just going on logic
            dateFrameOriginal.reading.plot(label =LegendLabelOriginal,color='g')
            dateFrameWeighted.plot(label = LegendLabelWeighted,color ='Y',marker ='o')

            if ((len(Title) > 0) and (len(YLabel)>0) and (len(XLabel) > 0)):
                plt.legend()
                plt.ylabel(YLabel)
                plt.xlabel(XLabel)
                plt.title(Title)
                FileToReturn = plt.savefig(fileName) #1
                # or
                plt.savefig(buffer) #2
        # Apparently this is a good alternative, the above is just a logical flow



        plot_data = buffer.getvalue()
        return FileToReturn
        # thus could either return file to return or
        return plot_data



    def turnDateFrameIntoGraph(self,dateFrameIn,amountOfWeight = 1,freqVal='1min',min_periodsVal=10,
                               Title="YourTitle",YLabel="Y",XLabel="X",fileName="plotted.svg",typeWeight = "EWMA"):
        """Specify the dateFrame that you want to plotted against its EMWA
        you require the parameters to shape the plot.
        The parameters are explained in the self.expoweightedresampling and self.plotDataBetweenTwoDateFrames
        fileName: This will be what you want to save the file as < not sure if I should keep this
        or hard code the fileName to keep consistency
        Return: This will attempt to return the file that stores the figured for the plot
        """
        dateFrameWeighted = None
        LegendToSend =""
        ## check length of typeWeight
        if (typeWeight == "EWMA"):
            dateFrameWeighted = self.expoweightedresampling(dateFrameIn,amountOfWeight,freqVal,min_periodsVal)
            LegendToSend= "Exponential weighted moving average plot"
        else:
            dateFrameWeighted = self.equalWeightMovingAverage(dateFrameIn,freqVal,min_periodsVal)
            LegendToSend= "Equal weighted moving average plot"

        return self.plotDataBetweenTwoDateFrames(dateFrameIn,dateFrameWeighted,LegendLabelWeighted=LegendToSend,
                                                 Title=Title,YLabel=YLabel,XLabel=XLabel,FileName =fileName)

    def equalWeightMovingAverage(self,dateFrameIn,freqVal='1min',min_periodsVal=10):
        """Specify the dateFrame that you want to plot
        :rtype : object
        freqVal: "1min","1H", "1M", "1S" or any multiples there of
        min_periodsVal: This is the number of values you need in order for this plot to be useful
        NOTE:
        The 1 minute frequency is the accepted min for frequency, even though if this is done over a few weeks
        would possibly want freq to be a few hours, will refactor for that case. This is v1.0

        Return: This will return a dateFrame resampled under the equal weight moving average principal
        """

        if (dateFrameIn == None):
            raise ValueError('Invalid DateFrame, Please pass DateFrame with actually data')
        if (min_periodsVal<= 0):
            raise ValueError("The min number of periods isn't valid")
        toReturn = None
        try:
            toReturn = pd.rolling_mean(dateFrameIn.reading,min_periodsVal,freqVal)
        except:
            raise ValueError("The frequency %d isn't valid for Pandas",freqVal)
        return toReturn

    def singlePlotOfFrame(self,dateFrameIn,Title="YourTitle",lengendLabel="plot 1",YLabel="Y",XLabel="X",
                                     fileName="plotted.svg"):
        """Specify the dateFrame that you want to plot, single dateFrame
        Title: The title for the plot : "THE BEST PLOT EVER"
        YLabel: The label for the y axis : reading(kWh)
        XLabel: The label for the x axis : Time Stamp
        fileName: file name you want to save as

        Return: return the figure or a stringIO of the figure
        """
        FileToReturn = None
        canSave = False
        splitted = fileName.split(".")
        buffer = StringIO()
        if ((splitted[1] == "svg") or (splitted[1] == "png") or (splitted[1] == "jpg") ):
            canSave = True # will add more
            #fig = plt.figure() # not needed # the below needs to still be tested, just going on logic
            if (len(lengendLabel) <= 0):
                lengendLabel="plot 1"

            dateFrameIn.reading.plot(label=lengendLabel,color='g') # should probably check if the plotting actually needs reading or not
            if (len(Title) <= 0):
                Title = "A plot"
            if ((len(YLabel)<=0)):
                YLabel = "Y"
            if (len(XLabel) <= 0):
                XLabel="X"


            plt.legend()
            plt.ylabel(YLabel)
            plt.xlabel(XLabel)
            plt.title(Title)
            FileToReturn = plt.savefig()
            # or
            plt.savefig(buffer)

        # Apparently this is a good alternative, the above is just a logical flow



        plot_data = buffer.getvalue()
        return FileToReturn
        # thus could either return file to return or
        return plot_data