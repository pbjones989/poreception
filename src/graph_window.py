import sys
import os
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
        varX = tk.StringVar()
        varX.set(self.xaxis)
        varY = tk.StringVar()
        varY.set(self.yaxis)
        var_group = tk.StringVar()
        var_group.set(self.group_category)
        options = {'mean', 'stdv', 'median', 'max', 'min', 'duration_obs'}
        group_options = {'channel', 'run'}
        layout = tk.PanedWindow(self, sashpad=4, sashrelief=tk.RAISED)
        control_panel = tk.Frame(layout, width=20)
        graph = tk.Frame(layout)
        layout.add(control_panel)
        layout.add(graph)
        layout.paneconfigure(control_panel, sticky='nw')
        layout.paneconfigure(graph, sticky='nse')
        layout.pack(fill='both', expand=True)

        xAxisSelect = tk.OptionMenu(control_panel, varX, *options, command=self.update_x_axis)
        yAxisSelect = tk.OptionMenu(control_panel, varY, *options, command=self.update_y_axis)
        group_select = tk.OptionMenu(control_panel, var_group, *group_options, command=self.update_group_category)
        clearSelected_button = tk.Button(control_panel, text='Unselect all', width=15, command=self.clear_selected)
        showRawData_button = tk.Button(control_panel, text='Show Raw Data', width=15, command=self.showRawData)
        deleteButton = tk.Button(control_panel, text='Delete Group', width=15, command=self.delete_group)
        undoButton = tk.Button(control_panel, text='Undo Last Deletion', width=15, command=self.undo_delete)
        self.deleteChannel = tk.Entry(control_panel)
        self.isBox = tk.IntVar()
        box_select_on = tk.Checkbutton(control_panel, text='Box Select', variable=self.isBox, command=self.activate_box)
        deleteUnselected = tk.Button(control_panel, text='Clear Unselected', width=15, command=self.delete_unselected)
        showHistogram_button = tk.Button(control_panel, text='Show Histogram', width=15, command=self.show_histogram)
        export_data_button = tk.Button(control_panel, text='Export Data', width=15, command=self.export_data)
        self.export_path = tk.Entry(control_panel)
        export_description = tk.Label(control_panel, text="Path to export to (including name)")
        deleteButton.pack()
        self.deleteChannel.pack()
        undoButton.pack()
        xAxisSelect.pack()
        yAxisSelect.pack()
        showRawData_button.pack()
        clearSelected_button.pack()
        box_select_on.pack()
        deleteUnselected.pack()
        showHistogram_button.pack()
        export_description.pack()
        self.export_path.pack()
        export_data_button.pack()
        group_select.pack()



        self.previousDataSets = []
        self.selected_points = set()
        self.raw_data = raw_data
        self.runs = df_runs
        self.original_runs = self.runs

        self.fig, self.ax = plt.subplots()

        xs = [self.runs.iloc[data][self.xaxis] for data in self.selected_points]
        ys = [self.runs.iloc[data][self.yaxis] for data in self.selected_points]
        self.selected, = self.ax.plot(xs, ys, 'o', ms=10, alpha=.8, color='red', visible=False)

        self.lines = []
        self.data = None
        self.regroup_data()
        self.ax.set_xlabel(self.xaxis)
        self.ax.set_ylabel(self.yaxis)
        canvas = FigureCanvasTkAgg(self.fig, graph)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill='both', expand=True)
        toolbar = NavigationToolbar2Tk(canvas, graph)
        toolbar.update()
        self.fig.canvas.mpl_connect('pick_event', self.onpick)

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

        self.rs = RectangleSelector(self.ax, self.line_select_callback, drawtype='box', useblit=True, interactive=True)
        self.rs.set_active(False)

    def export_data(self):
        path = self.export_path.get()
        raw_path = path + "_raw_data"
        summary_path = path + "_summary_data.pkl"
        rows = []
        for i in range(0, len(self.runs.index)):
            index = int(self.runs.iloc[i, :].name)
            rows.append(self.raw_data[index])
        export_raw = np.asarray(rows)
        np.save(raw_path, export_raw)
        export_runs = self.runs.reset_index(drop=True)
        export_runs.to_pickle(summary_path)

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
        if self.isBox.get():
            self.rs.set_active(True)
        else:
            self.rs.set_active(False)

    def hover(self, event):
        if not self.isBox.get():
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
        if self.isBox.get():
            x_1, y_1 = eclick.xdata, eclick.ydata
            x_2, y_2 = erelease.xdata, erelease.ydata
            for i in range(0, len(self.runs.index)):
                index = int(self.runs.iloc[i, :].name)
                row = self.original_runs.iloc[index, :]
                if row[self.xaxis] >= x_1 and row[self.xaxis] <= x_2 and row[self.yaxis] >= y_1 and row[self.yaxis] <= y_2:
                    self.selected_points.add(index)
            self.update()

    def delete_group(self, to_delete=None):
        if not to_delete:
            to_delete = []
            if self.group_category == 'channel':
                to_delete = [int(name.strip()) for name in self.deleteChannel.get().split(',')]
            else:
                to_delete = [name.strip() for name in self.deleteChannel.get().split(',')]
        for name in to_delete:
            if name in self.data.groups:
                oldRuns = self.runs
                self.runs = self.data.filter(lambda x : x.name != name)
                self.data = self.runs.groupby(self.group_category)
                self.previousDataSets.append(oldRuns)
        self.update_lines()

    def delete_unselected(self):
        oldRuns = self.runs
        for index, row in self.runs.iterrows():
            if int(row.name) not in self.selected_points:
                self.runs = self.runs.drop(index)
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
        xs = [self.original_runs.iloc[data][self.xaxis] for data in self.selected_points]
        ys = [self.original_runs.iloc[data][self.yaxis] for data in self.selected_points]
        self.selected.set_data(xs, ys)
        self.fig.canvas.draw()

