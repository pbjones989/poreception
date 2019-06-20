import sys
import time
import os
import h5py
import tkinter as tk
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from tkinter.filedialog import askopenfilename
from matplotlib.widgets import RectangleSelector
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from raw_data_window import RawDataWindow
from histogram_window import HistogramWindow

class GraphWindow(tk.Toplevel):
    def __init__(self, parent, df_runs, raw_data, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.xaxis = 'mean'
        self.yaxis = 'stdv'
        self.group_category = 'channel'
        var_x = tk.StringVar()
        var_x.set(self.xaxis)
        var_y = tk.StringVar()
        var_y.set(self.yaxis)
        var_group = tk.StringVar()
        var_group.set(self.group_category)
        options = {'mean', 'stdv', 'median', 'max', 'min', 'duration_obs'}
        group_options = {'channel', 'run'}

        # General control
        control_frame = tk.Frame(self, borderwidth=1, relief="solid")
        x_axis_label = tk.Label(control_frame, text='x axis:')
        x_axis_select = tk.OptionMenu(control_frame, var_x, *options, command=self.update_x_axis)
        y_axis_label = tk.Label(control_frame, text='y axis:')
        y_axis_select = tk.OptionMenu(control_frame, var_y, *options, command=self.update_y_axis)
        group_label = tk.Label(control_frame, text='Group by:')
        group_select = tk.OptionMenu(control_frame, var_group, *group_options, command=self.update_group_category)
        undo_button = tk.Button(control_frame, text='Undo Last Deletion', width=15, command=self.undo_delete)
        show_histogram_button = tk.Button(control_frame, text='Show Histogram', width=15, command=self.show_histogram)

        x_axis_label.grid(row=0, column=0)
        x_axis_select.grid(row=0, column=1)
        y_axis_label.grid(row=0, column=2)
        y_axis_select.grid(row=0, column=3)
        group_label.grid(row=0, column=4)
        group_select.grid(row=0, column=5)
        undo_button.grid(row=1, column=0, columnspan=3, sticky='s')
        show_histogram_button.grid(row=1, column=3, columnspan=3, sticky='s')

        # Group Deletion
        delete_frame = tk.Frame(self, borderwidth=1, relief="solid")
        group_delete_label = tk.Label(delete_frame, text='Groups to delete:')
        self.channel_to_delete = tk.Entry(delete_frame)
        delete_button = tk.Button(delete_frame, text='Delete Groups', width=15, command=self.delete_group)

        group_delete_label.grid(row=0, column=0)
        self.channel_to_delete.grid(row=1, column=0)
        delete_button.grid(row=2, column=0, sticky='s')

        
        # Selection
        selection_frame = tk.Frame(self, borderwidth=1, relief="solid")
        clear_selected_button = tk.Button(selection_frame, text='Unselect all', width=15, command=self.clear_selected)
        show_raw_data_button = tk.Button(selection_frame, text='Show Raw Data', width=15, command=self.showRawData)
        self.is_box = tk.IntVar()
        box_select_on = tk.Checkbutton(selection_frame, text='Box Select', variable=self.is_box, command=self.activate_box)
        delete_unselected_button = tk.Button(selection_frame, text='Delete Unselected', width=15, command=self.delete_unselected)
       
        clear_selected_button.grid(row=0, column=0)
        show_raw_data_button.grid(row=1, column=0)
        delete_unselected_button.grid(row=2, column=0, sticky='s')
        box_select_on.grid(row=1, column=1)


        # Exporting Data
        export_frame = tk.Frame(self, borderwidth=1, relief="solid")
        export_data_button = tk.Button(export_frame, text='Export Data', width=15, command=self.export_data)
        self.export_path = tk.Entry(export_frame)
        export_description = tk.Label(export_frame, text="Path to export to (including name)")
        export_description.grid(row=0, column=0)
        self.export_path.grid(row=0, column=1)
        export_data_button.grid(row=1, column=0, columnspan=2, sticky='s')


        # initialize necessary data
        self.previousDataSets = []
        self.selected_points = set()
        self.raw_data = raw_data
        self.runs = df_runs
        self.original_runs = self.runs

        # set up graph and selected points
        self.fig, self.ax = plt.subplots()
        xs = [self.original_runs.at[data, self.xaxis] for data in self.selected_points]
        ys = [self.original_runs.at[data, self.yaxis] for data in self.selected_points]
        self.selected, = self.ax.plot(xs, ys, 'o', ms=10, alpha=.8, color='red', visible=False)
        self.lines = []
        self.data = None
        self.regroup_data()
        self.ax.set_xlabel(self.xaxis)
        self.ax.set_ylabel(self.yaxis)

        # initialize canvas and toolbar frame
        canvas = FigureCanvasTkAgg(self.fig, self)
        canvas.draw()
        toolbar_frame = tk.Frame(self)
        self.toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        self.toolbar.focus()
        self.toolbar.update()

        # canvas events
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
        self.rs = RectangleSelector(self.ax, self.line_select_callback, drawtype='box', useblit=True, interactive=True)
        self.rs.set_active(False)

        # Top level grid layout
        control_frame.grid(row=0, column=0, sticky="nsew")
        delete_frame.grid(row=0, column=1, sticky="nsew")
        selection_frame.grid(row=0, column=2, sticky="nsew")
        export_frame.grid(row=0, column=3, sticky="nsew")
        toolbar_frame.grid(row=1, column=0, columnspan=4, sticky="s")
        canvas.get_tk_widget().grid(row=2, column=0, columnspan=4, sticky="nsew")

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=6)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)


    def export_data(self):
        new_file_name = self.export_path.get() + ".hdf5"
        export_runs = self.runs.reset_index(drop=True)
        export_runs.to_hdf(new_file_name, key="summary", mode="w")
        new_file = h5py.File(new_file_name, "a")
        new_grp = new_file.create_group('raw')
        for i in range(0, len(self.runs.index)):
            index = int(self.runs.iloc[i, :].name)
            new_grp.create_dataset(str(i), data=self.raw_data[index])

    def regroup_data(self):
        self.data = self.runs.groupby(self.group_category)
        for line in self.lines:
            line.remove()
            del line
        self.lines = []
        for label, group in self.data:
            line, = self.ax.plot(group[self.xaxis], group[self.yaxis], 'o', ms=3, alpha=.3, picker=2, label=label)
            self.lines.append(line)
        self.update_axes()

    def update_annot(self, dataind, line):
        label = self.get_label_from_artist(line)
        currData = self.data.get_group(label).iloc[dataind["ind"][0]]
        newPoint = int(currData.name)
        text = self.group_category + ": " + str(label) + ", index: " + str(newPoint)

        self.annot.xy = (currData[self.xaxis], currData[self.yaxis])
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.4)

    def show_histogram(self):
        self.histogram = HistogramWindow(self, self.runs)

    def activate_box(self):
        if self.is_box.get():
            self.rs.set_active(True)
        else:
            self.rs.set_active(False)

    def hover(self, event):
        if not self.is_box.get():
            found = False
            for line in self.lines:
                cont, ind = line.contains(event)
                if cont:
                    self.update_annot(ind, line)
                    self.annot.set_visible(True)
                    self.fig.canvas.draw_idle()
                    found = True

            if self.annot.get_visible() and not found:
                self.annot.set_visible(False)
                self.fig.canvas.draw_idle()

    def line_select_callback(self, eclick, erelease):
        if self.is_box.get():
            x_1, y_1 = eclick.xdata, eclick.ydata
            x_2, y_2 = erelease.xdata, erelease.ydata
            self.selected_points.update(self.runs[(self.runs[self.xaxis] >= x_1) & (self.runs[self.xaxis] <= x_2) \
                                                    & (self.runs[self.yaxis] >= y_1) & (self.runs[self.yaxis] <= y_2)].index)
            self.update()

    def delete_group(self, to_delete=None):
        if not to_delete:
            to_delete = []
            if self.group_category == 'channel':
                to_delete = [int(name.strip()) for name in self.channel_to_delete.get().split(',')]
            else:
                to_delete = [name.strip() for name in self.channel_to_delete.get().split(',')]
        for name in to_delete:
            if name in self.data.groups:
                # RESET INDEX?
                oldRuns = self.runs
                self.runs = self.runs[self.runs[self.group_category] != name]
                self.data = self.runs.groupby(self.group_category)
                self.previousDataSets.append(oldRuns)
        self.update_lines()

    def update_runs(self, new_runs):
        oldRuns = self.runs
        self.runs = new_runs
        self.data = self.runs.groupby(self.group_category)
        self.previousDataSets.append(oldRuns)
        self.update_lines()
    
    def delete_unselected(self):
        oldRuns = self.runs
        toKeep = [i in self.selected_points for i in range(0, len(self.runs.index))]
        self.runs = self.runs.loc[toKeep]
        self.data = self.runs.groupby(self.group_category)
        self.previousDataSets.append(oldRuns)
        self.update_lines()

    def undo_delete(self):
        if self.previousDataSets:
            self.runs = self.previousDataSets.pop()
            self.data = self.runs.groupby(self.group_category)
        self.update_lines()

    def clear_selected(self):
        self.selected_points.clear()
        self.update()

    def showRawData(self):
        if self.selected_points:
            indices = list(self.selected_points)
            self.rawDataWindow = RawDataWindow(self, self.raw_data, indices)

    def onpick(self, event):
        if event.artist not in self.lines:
            return True
        N = len(event.ind)
        if not N:
            return True

        label = self.get_label_from_artist(event.artist)

        dataind = event.ind[0]
        currData = self.data.get_group(label).iloc[dataind]
        newPoint = int(currData.name)
        if newPoint in self.selected_points:
            self.selected_points.remove(newPoint)
        else:
            self.selected_points.add(newPoint)
        self.update()

    def update_lines(self):
        for line in self.lines:
            label = self.get_label_from_artist(line)
            if label in self.data.groups:
                currGroup = self.data.get_group(label)
                line.set_data(currGroup[self.xaxis], currGroup[self.yaxis])
            else:
                line.set_data([], [])
        self.update()

    def update_x_axis(self, new_value):
        self.xaxis = new_value
        self.update_axes()

    def update_y_axis(self, new_value):
        self.yaxis = new_value
        self.update_axes()

    def update_group_category(self, new_value):
        self.group_category = new_value
        self.regroup_data()

    def update_axes(self):
        maxY = self.data[self.yaxis].max().max()
        maxX = self.data[self.xaxis].max().max()
        minX = self.data[self.xaxis].min().min()
        minY = self.data[self.yaxis].min().min()
        xDif = (maxX - minX) / 10
        yDif = (maxY - minY) / 10
        self.ax.set_xlim(minX - xDif, maxX + xDif)
        self.ax.set_ylim(minY - yDif, maxY + yDif)
        self.ax.set_xlabel(self.xaxis)
        self.ax.set_ylabel(self.yaxis)
        self.update_lines()

    def get_label_from_artist(self, artist):
        label = artist.get_label()
        if self.group_category == 'channel':
            label = int(label)
        return label

    def update(self):
        self.selected.set_visible(True)
        xs = [self.original_runs.at[data, self.xaxis] for data in self.selected_points]
        ys = [self.original_runs.at[data, self.yaxis] for data in self.selected_points]
        self.selected.set_data(xs, ys)
        self.fig.canvas.draw()

