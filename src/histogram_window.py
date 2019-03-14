import sys
import os
import tkinter as tk
from tkinter import messagebox
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from tkinter.filedialog import askopenfilename
from matplotlib.widgets import RectangleSelector
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class HistogramWindow(tk.Toplevel):
    def __init__(self, parent, df_runs, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.data = df_runs
        self.fig, self.ax = plt.subplots()
        self.x_statistic = 'channel'
        self.counts, self.bins, self.bars = self.ax.hist(df_runs[self.x_statistic], edgecolor='black', bins=512)

        hist_var = tk.StringVar()
        hist_var.set(self.x_statistic)
        options = {'channel', 'mean', 'stdv', 'median', 'max', 'min', 'duration_obs'}
        self.histogram_select = tk.OptionMenu(self, hist_var, *options, command=self.change_histogram)
        self.histogram_select.pack()

        canvas = FigureCanvasTkAgg(self.fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()

        self.data_label = self.ax.text(0.8, 0.8, self.x_statistic + ': ', verticalalignment='center',
                                          horizontalalignment='center', transform=self.ax.transAxes)
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

    def hover(self, event):
        for bar in self.bars:
            cont, ind = bar.contains(event)
            if cont:
                label = ''
                if self.x_statistic == 'channel':
                    label = str(self.bars.index(bar) + 1)
                else:
                    label = str(round(self.bins[self.bars.index(bar)],2))
                self.data_label.set_text(self.x_statistic + ': ' + label)
                self.fig.canvas.draw()

    def change_histogram(self, new_value):
        self.ax.cla()
        self.x_statistic = new_value
        if (self.x_statistic == 'channel'):
            self.counts, self.bins, self.bars = self.ax.hist(self.data[self.x_statistic], edgecolor='black', bins=512)
        else:
            self.counts, self.bins, self.bars = self.ax.hist(self.data[self.x_statistic], edgecolor='black', bins=20)

        self.data_label = self.ax.text(0.8, 0.8, self.x_statistic + ': ', verticalalignment='center',
                                          horizontalalignment='center', transform=self.ax.transAxes)
        self.fig.canvas.draw()

