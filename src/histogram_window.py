import matplotlib
import numpy as np
import os
import pandas as pd
import sys
import tkinter as tk
from tkinter import messagebox
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
        self.counts, self.bins, self.bars = self.plot_by_run()

        hist_var = tk.StringVar()
        hist_var.set(self.x_statistic)
        options = {'channel', 'mean', 'stdv', 'median', 'max', 'min', 'duration_obs'}
        histogram_select = tk.OptionMenu(self, hist_var, *options, command=self.change_histogram)
        channel_cutoff_label = tk.Label(self, text='Channel Cutoff:')
        self.channel_cutoff = tk.Entry(self)
        delete_channel_cutoff = tk.Button(self, text='Delete Above Cutoff', command=self.delete_above_cutoff)
        range_lower_label = tk.Label(self, text='Statistic Range Lower:')
        self.range_lower = tk.Entry(self)
        range_upper_label = tk.Label(self, text='Statistic Range Upper:')
        self.range_upper = tk.Entry(self)
        delete_range = tk.Button(self, text='Delete Specified Range', command=self.delete_in_range)
        histogram_select.grid(row=0, column=0)
        channel_cutoff_label.grid(row=0, column=1)
        self.channel_cutoff.grid(row=0, column=2, columnspan=3)
        delete_channel_cutoff.grid(row=0, column=5)

        range_lower_label.grid(row=1, column=1)
        self.range_lower.grid(row=1, column=2)
        range_upper_label.grid(row=1, column=3)
        self.range_upper.grid(row=1, column=4)
        delete_range.grid(row=1, column=5)

        canvas = FigureCanvasTkAgg(self.fig, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=3, column=0, columnspan=6)
        toolbar_frame = tk.Frame(self)
        toolbar_frame.grid(row=2, column=0, columnspan=6)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()

        self.data_label = self.ax.text(0.8, 0.8, self.x_statistic + ': ', verticalalignment='center',
                                          horizontalalignment='center', transform=self.ax.transAxes)
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

    def hover(self, event):
        for bar_container in self.bars:
            cont = any(bar.contains(event)[0] for bar in bar_container)
            if cont:
                label = ''
                if self.x_statistic == 'channel':
                    label = str(self.bars.index(bar_container) + 1)
                else:
                    label = str(round(self.bins[self.bars.index(bar_container)],2))
                self.data_label.set_text(self.x_statistic + ': ' + label)
                self.fig.canvas.draw()

    def delete_above_cutoff(self):
        if self.x_statistic == 'channel':
            cutoff = self.channel_cutoff.get()
            try:
                # TODO This is terrible
                cutoff = float(cutoff)
                to_keep = self.parent.runs
                for run, group in self.data.groupby('run'):
                    for channel, subgroup in group.groupby('channel'):
                        if len(subgroup.index) >= cutoff:
                            to_keep = to_keep[(to_keep['run'] != run) | (to_keep['channel'] != channel)]
                self.parent.update_runs(to_keep)
                self.data = to_keep
                self.change_histogram(self.x_statistic)
            except ValueError:
                messagebox.showinfo("Cutoff must be a number")

    def delete_in_range(self):
        if self.x_statistic != 'channel':
            lower = self.range_lower.get()
            upper = self.range_upper.get()
            try:
                # TODO: Not done here lol
                xmin, xmax, ymin, ymax = self.ax.axis()
                lower = xmin if isinstance(lower, str) and lower.lower() == 'min' else float(lower)
                upper = xmax if isinstance(upper, str) and upper.lower() == 'max' else float(upper)
                to_keep = self.parent.runs[(self.parent.runs[self.x_statistic] < lower) | \
                                           (self.parent.runs[self.x_statistic] > upper)]
                self.parent.update_runs(to_keep)
                self.data = to_keep
                self.change_histogram(self.x_statistic)
            except ValueError:
                messagebox.showinfo("Cutoff must be a number")

    def plot_by_run(self):
        run_groups = self.data.groupby('run')
        plot_groups = [run_groups.get_group(key)[self.x_statistic] for key in run_groups.groups.keys()]
        plot_groups.append([])
        bins = 512 if self.x_statistic == 'channel' else 20
        result = self.ax.hist(plot_groups, bins=bins)
        self.ax.legend(run_groups.groups.keys())
        return result

    def change_histogram(self, new_value):
        self.ax.cla()
        self.x_statistic = new_value
        if self.x_statistic == 'channel':
            self.channel_cutoff.config(state=tk.NORMAL)
            self.range_upper.config(state=tk.DISABLED)
            self.range_lower.config(state=tk.DISABLED)
        else:
            self.channel_cutoff.config(state=tk.DISABLED)
            self.range_upper.config(state=tk.NORMAL)
            self.range_lower.config(state=tk.NORMAL)

        self.counts, self.bins, self.bars = self.plot_by_run()
        self.data_label = self.ax.text(0.8, 0.8, self.x_statistic + ': ', verticalalignment='center',
                                          horizontalalignment='center', transform=self.ax.transAxes)
        self.fig.canvas.draw()

