__author__ = 'Vincent'
# This class will resample the data depending on different needs
import pandas as pd
import numpy as np
class Resampling():
    """Resampler."""

    def __init__(self):
        """Stuff that must be initialized when this class is created"""


    def downsampleDateFrame(self,dateFrameIn,freq="1min",closedVal = "left",labelVal="left",kindVal ="timestamp",howVal = None):
        """Specify the dateFrame that you want to resample to allow graphs to be not overfilled.
        freq: "1min","1H", "1M", "1S" or any multiples there of
        closed: this shows which side to include in the down sampling. ie, "left", "right"
        label: this is to show how the time stamps will be labelled from. ie, "left", "right"
        kind: Either timestamp or period depending on your need, generally time stamp works better

        Example: downsample(df,freq="5min",closed ="left",label= "left",how ="mean")
        This will then resample the dataframe df into 5 minute intervals and the intervals will be
        recalculated using the mean of the interval. The left value of the interval is excluded
        the timestamp will start on the left side of the interval.

        #df2.resample('1min',how='mean',axis = 0,closed ='right',label = 'left',kind ='timestamp')

        Returns a pandas DataFrame object with name which is the timestamp, it will have
        a reading column, this DataFrame will be resampled the way you need it to be"""

        #this is the resample method
        # Ask kevin about checking type to dataFrame
        # if (type(dateFrameIn) == pd.DateFrame):

        if (dateFrameIn == None):
            raise ValueError('Invalid DateFrame, Please pass DateFrame with actually data')
        if (not(closedVal.__eq__("left")) or not(closedVal.__eq__("right"))):
            raise ValueError("The closed side is incorrect, either it's left or right")
        if (not(labelVal.__eq__("left")) or not(labelVal.__eq__("right"))):
            raise ValueError("The label is incorrect, either it's left or right")
        if (not(kindVal.__eq__("timestamp")) or not(kindVal.__eq__("period"))):
            if (not(kindVal == None)):
                raise ValueError("The kind of DateFrame is incorrect, please input the correct type")

        toReturn = None
        try:
            toReturn = dateFrameIn.resample(freq,how= howVal,closed= closedVal,label= labelVal,kind= kindVal)
        except:
            raise ValueError("The frequency inputted isn't one that Pandas can identify, please input correct frequency")

        return toReturn

        #dateFrameIn.resample('1min',how='mean',axis = 0,closed ='right',label = 'left',kind ='timestamp')
    def getmaxminforgraphing(self,dateFrameIn,column="reading"):
        """
        This will take a Pandas DateFrame
        column: You can choose what column you want to find max and min value
        max, min: just so you can get multiple values from this method back
        :return: no specific return, this will be done via parameters max, min
        """

        if (dateFrameIn == None):
            raise ValueError('Invalid DateFrame, Please pass DateFrame with actually data')
        try:
            columnArray = dateFrameIn.ix[:,column] #check column
            #print(maxCollumn)
            max = 0
            if (len(columnArray) == 0):
                raise ValueError("There isn't any data to calculate a min and max")

            for x in range(0, len(columnArray)):
                if (max < columnArray[x]):
                    max = columnArray[x]

            min = max
            for x in range(0, len(columnArray)):
                if (min > columnArray[x]):
                    min = columnArray[x]
            yield min, max  # return the min and max values
            ## return int array
        except:
            raise ValueError("The column %s specified doesn't exist in this Pandas DateFrame",column)

    def getmoreaccuratestd(self,dateFrameIn,column="reading"):
        """
        This will take a Pandas DateFrame
        :return: This will return a Standard Deviation of the Pandas DateFrame with higher accuracy
        """
        if (dateFrameIn == None):
            raise ValueError('Invalid DateFrame, Please pass DateFrame with actually data')
        columnArray = None
        try:
            columnArray = dateFrameIn.ix[:,column]
        except:
            raise ValueError("The column %s doesn't exist in the provided DateFrame",column)

        npaColumnArray = np.array(columnArray)
        stdworked = npaColumnArray.std()
        if (stdworked == 0):
            raise ValueError("Please input a DateFrame with actual data in")

        return stdworked

    def getDateFrameStd(self,dateFrameIn,column="reading"):
        """
        This will take a Pandas DateFrame this dataFrame should be resampled
        :return: This will return a Standard Deviation of the Pandas DateFrame
        """
        if not dateFrameIn:
            raise ValueError('Invalid DateFrame, Please pass DateFrame with actually data')
        stdworked = 0
        if (len(column) <= 0):
            raise ValueError("Invalid column value to find std on")

        try:
            stdworked = dateFrameIn.std(column)
        except:
            raise ValueError("The column %s doesn't exist in the provided DateFrame",column)

        if (stdworked == 0):
            raise ValueError("Please input a DateFrame with actual data in")

        return stdworked

    def getListOfOutliers(self,dateFrameIn,freq="1min",closedVal = "left",labelVal="left",kindVal ="timestamp",column="reading"):
        """
        This will take a Pandas DateFrame this dataFrame should be resampled
        freq,closedVal,LabelVal,kindVal,howVal: are for the resampling and will be handled by the method
        downsampleDateFrame, this will raise a valueError
        column: This is the column you want to see outliers on, generally will be the "reading" column
        Reason for duplicating the default values is for less error checking and can call the downSampleDataFrame method
        without any concern
        :return: This will return list of DateTime that will be all the outliers
        """
        if not dateFrameIn:
            raise ValueError('Invalid DateFrame, Please pass DateFrame with actually data')
        DateFrameMean = None
        try:
            DateFrameMean = self.downsampleDateFrame(dateFrameIn,freq,closedVal,labelVal,kindVal,howVal="mean")
        except:
            raise ValueError("One of the parameters is incorrect")
        DateFrameOriginal = None

        try:
            DateFrameOriginal = self.downsampleDateFrame(dateFrameIn,freq,closedVal,labelVal,kindVal)
        except:
            raise ValueError("One of the parameters is incorrect")

        stdworked = 0

        try:
            stdworked = self.getmoreaccuratestd(dateFrameIn,column)
        except:
            raise ValueError("The column doesn't exist")

        toBeOutlier = 3*stdworked

        # Two arrays to get the outliers, the arrays allow us to compare values directly
        # No try is used because if it failed before on column, would fail again

        ArrOfMean = DateFrameMean.ix[:,column]
        arrTrueValue = DateFrameOriginal.ix[:,column]
        dateTimeList = []

        for x in range(0, len(ArrOfMean)-1):
            difference = arrTrueValue[x] - ArrOfMean[x]
            if (difference >= toBeOutlier):
                dateTimeList.append(str(dateFrameIn.ix[x]))

        return dateTimeList

