__author__ = 'Vincent'
import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt
import io
import Resampling as rs
import PIL

class Plotter:
    """Plotter"""
    GraphColorGreen = "#66FF00"
    GraphColorBlue = "#3366CC"
    AlertRed ="#FF0000"
    AlertOrange="#FF6600"
    AlertGreen="#339900"

    GraphFun = "#6F0"
    def __init__(self):
        """Stuff that must be initialized when this class is created"""

    @staticmethod
    def ewma_resampling(data_frame, freq='1min', min_periods=10):
        """Specify the dataFrame that you want to plot
        :rtype : object
        freq: "1min","1H", "1M", "1S" or any multiples thereof
        weight: This is how much does the observation affect the exponentially weighted mean
        min_periods: This is the number of values you need in order for this plot to be useful

        NOTE:
        The 1 minute frequency is the accepted min for frequency, even though if this is done over a few weeks
        would possibly want freq to be a few hours, will refactor for that case. This is v1.0

        Return: This will return a dataFrame resampled under the Exponential weight moving average principal
        """
        if data_frame is None:
            raise ValueError("Invalid dataFrame, pass a DataFrame with actual data")
        if min_periods <= 0:
            raise ValueError("The min number of periods is invalid, should be a float >0")
        weight = (len(data_frame)-1)/2
        # review comments: don't replace a potentially meaningful exception with one that only guesses what the problem is
        return pd.ewma(data_frame.reading, com=weight, freq=freq)


    def plot_two_data_frames(self,unweighted_data_frame, weighted_data_frame, y_label=None, x_label=None,
                             unweighted_legend=None, weighted_legend=None, title=None, file_name=None):
        """Specify the dataFrame that you want to plot, a weighted vs actual readings currently
        Title: A string title for the plot
        XLabel: The label for the x axis : Time Stamp
        YLabel: The label for the y axis : reading(kWh)
        fileName: file name you want to save as

        Return: return the figure or a stringIO of the figure if no filename is given
        """
        # Review comments: How does this end up in the plt object? Don't have docs to check
        unweighted_data_frame.reading.plot(label=unweighted_legend, color=self.GraphColorGreen, linewidth=0.5)
        weighted_data_frame.plot(label=weighted_legend, color=self.GraphColorBlue, marker='o', linewidth=0.5)

        if title:
            plt.title(title)
        if y_label:
            plt.ylabel(y_label)
        if x_label:
            plt.xlabel(x_label)

        if unweighted_legend or weighted_legend:  # What is the purpose of this?
            plt.legend()

        if not file_name:
            file_buffer = io.BytesIO()
            plt.savefig(file_buffer)
            return file_buffer.getvalue()
        else:
            file_name_split = file_name.split(".")
            if (file_name_split[-1] == "svg") or (file_name_split[-1] == "png") or (file_name_split[-1] == "jpg"):
                return plt.savefig(file_name)
            else:
                return None

    def plot_data_frame_vs_ewma(self, data_frame, weight=1, freq='1min', min_periods=10, title=None, y_label=None, x_label=None,
                        file_name=None, weight_type='ewma'):
        """Specify the dataFrame that you want to plotted against its EMWA
        you require the parameters to shape the plot.
        The parameters are explained in the self.expoweightedresampling and self.plotDataBetweenTwodataFrames
        file_name: This will be what you want to save the file as < not sure if I should keep this
        or hard code the fileName to keep consistency
        Return: This will attempt to return the file that stores the figure for the plot
        """
        # # check length of typeWeight
        if weight_type == 'ewma':
            weighted_data_frame = self.ewma_resampling(data_frame, weight, freq)
            #print weighted_data_frame
            legend = "Weighted Average plot"
        else:
            weighted_data_frame = self.equal_weight_moving_average(data_frame, freq, min_periods)
            legend = "Rolling Average plot"

        return self.plot_two_data_frames(unweighted_data_frame=data_frame, weighted_data_frame=weighted_data_frame,
                                         weighted_legend=legend, title=title,y_label=y_label, x_label=x_label,
                                         file_name=file_name)

    @staticmethod
    def equal_weight_moving_average(data_frame, freq='1min', min_periods=10):
        """ Resamples data using a rolling mean
        :rtype : object
        freq: "1min","1H", "1M", "1S" or any multiples there of
        min_periods: This is the number of values you need in order for this plot to be useful
        NOTE:
        The 1 minute frequency is the accepted min for frequency, even though if this is done over a few weeks
        would possibly want freq to be a few hours, will refactor for that case. This is v1.0

        Return: This will return a dataFrame resampled under the equal weight moving average principal
        """

        if not data_frame:
            raise ValueError('Invalid dataFrame, Please pass dataFrame with actual data')
        if min_periods < 1:
            raise ValueError("The min number of periods is invalid")
        # Review comments: same as before
        result = pd.rolling_mean(data_frame.reading, min_periods, freq)
        return result


    def plot_single_frame(self,data_frame, title=None, legend=None, y_label=None, x_label=None, file_name=None,
                          prediction=False,file_type="png"):
        """Specify the dataFrame that you want to plot, single dataFrame
        title: The string title for the plot
        y_label: The label for the y axis
        x_label: The label for the x axis
        file_name: file name you want to save as or None for a stringIO
        prediction: Make this true if plotting a prediction plot
        Return: return the figure or a stringIO of the figure
        """
        # Review comments: How does this end up in the plt object? Don't have docs to check
        if not prediction:
            data_frame.reading.plot(label=legend, color=self.GraphColorGreen)
        else:
            data_frame.plot(label=legend, color='b')    # This is to handle plotting forecast data
        if title:
            plt.title(title)
        if y_label:
            plt.ylabel(y_label)
        if x_label:
            plt.xlabel(x_label)
        if legend:
            plt.legend()

        if not file_name:   # if file_name is None
            if (not(file_type.__eq__("bmp") or file_type.__eq__("png") or file_type.__eq__("jpg"))):
                file_type = "png"
            buf = io.BytesIO()
            plt.savefig(buf, format = file_type,bbox_inches ="tight",dpi = 300,facecolor ="w",edgecolor="g")
            buf.seek(0)
            im = PIL.Image.open(buf)
            # possibly should use save fig
            return im
        else:
            file_name_split = file_name.split(".")
            if (file_name_split[-1] == "svg") or (file_name_split[-1] == "png") or (file_name_split[-1] == "jpg"):
                return plt.savefig(file_name)
            else:
                return None

    def plot_single_frame_unusual(self,data_frame,freq="1min", title=None, legend=None, y_label=None, x_label=None, file_name=None,
                          prediction=False,file_type="png"):
        """Specify the dataFrame that you want to plot, single dataFrame
        title: The string title for the plot
        y_label: The label for the y axis
        x_label: The label for the x axis
        file_name: file name you want to save as or None for a stringIO
        prediction: Make this true if plotting a prediction plot
        Return: return the figure or a stringIO of the figure
        """
        # Review comments: How does this end up in the plt object? Don't have docs to check

        if data_frame is None:
            raise ValueError('Invalid DateFrame, Please pass DateFrame with actually data')

        try:
            data_frame = rs.Resampling().downsample_data_frame(data_frame, freq)
            data_frameWeighted = self.ewma_resampling(data_frame=data_frame, freq=freq,min_periods=1)
        except:
            raise ValueError("One of the parameters is incorrect")


        #data_frame.reading.plot(label=legend, color=self.GraphColorGreen,sharex=True,marker="o")
            # This is to handle plotting forecast data
        if title:
            plt.title(title)
        if y_label:
            plt.ylabel(y_label)
        if x_label:
            plt.xlabel(x_label)
        if legend:
            plt.legend()
        data_frameWeighted = pd.DataFrame(data_frameWeighted,columns=("reading",))
        #data_frameWeighted.reading.plot()

        std = rs.Resampling().get_frame_std_dev(data_frame=data_frameWeighted)
        toRed = std*3
        toOrange = std*1.75

        means = data_frameWeighted.ix[:, "reading"]
        true_values = data_frame.ix[:, "reading"]



        #single.reading.plot(color=self.AlertOrange,marker='o',markerfacecolor=self.AlertOrange)
        single = []
        for x in range(len(true_values)):
            difference = true_values[x] - means[x]
            difference = abs(difference)
            if (difference < toOrange):
                plottedColor = self.AlertGreen
            elif (difference>=toRed):
                plottedColor = self.AlertRed
            else:
                plottedColor = self.AlertOrange
            single.append(plottedColor)

        data_frame.reading.plot(kind='bar',label=legend,sharex=True,color=single,grid=False)
        #data_frame.reading.bar(label=legend,color= self.GraphColorGreen)
        #data_frame.reading.plot(label=legend,color= self.GraphColorGreen)
        #data_frame.reading.plot(label=legend)
        #plt.show()
        plt.ylabel("Usage(kwh)")
        plt.xlabel("timestamp")
        plt.title("unusual plot")
        #print(data_frame["reading"])
        #plt.scatter(data_frame.index,data_frame["reading"],marker="o")
        #data_frame["reading",0].plot(style='.')
        if not file_name:   # if file_name is None
            if (not(file_type.__eq__("bmp") or file_type.__eq__("png") or file_type.__eq__("jpg"))):
                file_type = "png"
            buf = io.BytesIO()
            plt.savefig(buf, format = file_type,bbox_inches ="tight",dpi = 300,facecolor ="w",edgecolor="g")
            buf.seek(0)
            im = PIL.Image.open(buf)
            # possibly should use save fig
            return im
        else:
            file_name_split = file_name.split(".")
            if (file_name_split[-1] == "svg") or (file_name_split[-1] == "png") or (file_name_split[-1] == "jpg"):
                return plt.savefig(file_name)
            else:
                return None