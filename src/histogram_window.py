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
        
        # General control
        control_frame = tk.Frame(self, borderwidth=1, relief="solid")
        hist_var = tk.StringVar()
        hist_var.set(self.x_statistic)
        options = {'channel', 'mean', 'stdv', 'median', 'max', 'min', 'duration_obs'}
        histogram_x_label = tk.Label(control_frame, text='x statistic:')
        histogram_select = tk.OptionMenu(control_frame, hist_var, *options, command=self.change_histogram)
        undo_delete_button = tk.Button(control_frame, text='Undo last deletion', command=self.undo_delete)
        
        histogram_select.grid(row=0, column=0)
        histogram_x_label.grid(row=0, column=1)
        undo_delete_button.grid(row=1, column=0, columnspan=2, sticky="s")

        # For deleting by Channel
        channel_delete_frame = tk.Frame(self, borderwidth=1, relief="solid")
        channel_cutoff_label = tk.Label(channel_delete_frame, text='Channel Cutoff:')
        self.channel_cutoff = tk.Entry(channel_delete_frame)
        delete_channel_cutoff = tk.Button(channel_delete_frame, text='Delete Above Cutoff', command=self.delete_above_cutoff)

        channel_cutoff_label.grid(row=0, column=0)
        self.channel_cutoff.grid(row=0, column=1)
        delete_channel_cutoff.grid(row=1, column=0, columnspan=2, sticky="s")

        # For deleting by range
        range_delete_frame = tk.Frame(self, borderwidth=1, relief="solid")
        range_run_label = tk.Label(range_delete_frame, text='Run:')
        self.range_run = tk.Entry(range_delete_frame)
        range_lower_label = tk.Label(range_delete_frame, text='Statistic Range Lower:')
        self.range_lower = tk.Entry(range_delete_frame)
        range_upper_label = tk.Label(range_delete_frame, text='Statistic Range Upper:')
        self.range_upper = tk.Entry(range_delete_frame)
        delete_range = tk.Button(range_delete_frame, text='Delete Specified Range', command=self.delete_in_range)

        range_run_label.grid(row=0, column=0, columnspan=2)
        self.range_run.grid(row=0, column=2, columnspan=2)
        range_lower_label.grid(row=1, column=0)
        self.range_lower.grid(row=1, column=1)
        range_upper_label.grid(row=1, column=2)
        self.range_upper.grid(row=1, column=3)
        delete_range.grid(row=2, column=0, columnspan=4)

        # Set up canvas
        # TODO: try expand=True
        canvas = FigureCanvasTkAgg(self.fig, self)
        canvas.draw()
        toolbar_frame = tk.Frame(self)
        self.toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        self.toolbar.focus()
        self.toolbar.update()

        # Top level grid layout
        control_frame.grid(row=0, column=0, sticky="ns")
        channel_delete_frame.grid(row=0, column=1, sticky="ns")
        range_delete_frame.grid(row=0, column=2, sticky="ns")
        toolbar_frame.grid(row=1, column=0, columnspan=3, sticky="s")
        canvas.get_tk_widget().grid(row=2, column=0, columnspan=3, sticky="nsew")



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
            run = self.range_run.get()
            try:
                xmin, xmax, ymin, ymax = self.ax.axis()
                lower = xmin if isinstance(lower, str) and lower.lower() == 'min' else float(lower)
                upper = xmax if isinstance(upper, str) and upper.lower() == 'max' else float(upper)
                to_keep = self.parent.runs[(self.parent.runs['run'] != run) |  \
                                           ((self.parent.runs[self.x_statistic] < lower) | \
                                           (self.parent.runs[self.x_statistic] > upper))]
                self.parent.update_runs(to_keep)
                self.data = to_keep
                self.change_histogram(self.x_statistic)
            except ValueError:
                messagebox.showinfo("Cutoff must be a number")

    def plot_by_run(self):
        run_groups = self.data.groupby('run')
        plot_groups = [run_groups.get_group(key)[self.x_statistic] for key in run_groups.groups.keys()]
        #plot_groups.append([])
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
        self.fig.canvas.draw()
        self.toolbar.focus()
        self.toolbar.update()
    
    def undo_delete(self):
        self.parent.undo_delete()
        self.data = self.parent.runs
        self.change_histogram(self.x_statistic)
