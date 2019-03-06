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


class ControlPanel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.root.title("Set Up")
        self.show_graph_button = tk.Button(self, text='Show Graph',
                                           command=self.show_graph)
        self.show_graph_button.grid(row=0)
        self.add_data_button = tk.Button(self, text='Add Data Set', command=self.add_data_set)
        self.remove_data_button = tk.Button(self, text='Remove Data Set', command=self.remove_data_set)
        self.add_data_button.grid(row=0, column=1)
        self.remove_data_button.grid(row=0, column=2)
        self.data_sets = []
        self.data_row = 1

    def show_graph(self):
        if self.data_sets:
            summary_data = pd.DataFrame()
            raw_data = []
            for menu_option in self.data_sets:
                if os.path.exists(menu_option.summary_directory) and os.path.exists(menu_option.raw_directory):
                    new_summary = np.load(menu_option.summary_directory, encoding = 'latin1')
                    if isinstance(new_summary['channel'][0], str):
                        new_summary['channel'] = new_summary['channel'].map(lambda s: int(s[8:]))
                    summary_data = summary_data.append(new_summary)
                    raw_data.extend(np.load(menu_option.raw_directory, encoding = 'latin1').tolist())
                else:
                    messagebox.showinfo("No File Found",
                            "Could not find data files\n    given summary: "
                            + menu_option.summary_directory +
                            "\n    given raw: " + menu_option.raw_directory)
                    return
            summary_data = summary_data.reset_index(drop=True)
            GraphWindow(self, summary_data, np.asarray(raw_data))

    def add_data_set(self):
        new_menu_option = MenuOptions(self)
        new_menu_option.grid(row=self.data_row, columnspan=3)
        self.data_row += 1
        self.data_sets.append(new_menu_option)

    def remove_data_set(self):
        if self.data_sets:
            old_menu_option = self.data_sets.pop()
            old_menu_option.grid_forget()
            old_menu_option.destroy()
            self.data_row -= 1

class MenuOptions(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.summary_label = tk.Label(self, text='Summary data file:', font='TkDefaultFont 13 bold')
        self.summary_text = tk.StringVar()
        self.summary_directory = tk.Label(self, textvariable=self.summary_text)
        self.summary_chooser = tk.Button(self, text='Choose Summary Data', command=self.choose_summary_data)
        self.raw_label = tk.Label(self, text='Raw data file:', font='TkDefaultFont 13 bold')
        self.raw_text = tk.StringVar()
        self.raw_directory = tk.Label(self, textvariable=self.raw_text)
        self.raw_chooser = tk.Button(self, text='Choose Raw Data', command=self.choose_raw_data)

        self.summary_label.grid(row=0, column=0)
        self.summary_directory.grid(row=0, column=1)
        self.summary_chooser.grid(row=0, column=2)
        self.raw_label.grid(row=0, column=3)
        self.raw_directory.grid(row=0, column=4)
        self.raw_chooser.grid(row=0, column=5)

        self.summary_directory = ""
        self.raw_directory = ""

    def choose_summary_data(self):
        self.summary_directory = askopenfilename(initialdir=os.getcwd())
        directory = (self.summary_directory[(self.summary_directory.rfind('/') + 1):]
                    if len(self.summary_directory) > 25 else self.summary_directory)
        self.summary_text.set(directory)

    def choose_raw_data(self):
        self.raw_directory = askopenfilename(initialdir=os.getcwd())
        directory = (self.raw_directory[(self.raw_directory.rfind('/') + 1):]
                    if len(self.raw_directory) > 25 else self.raw_directory)
        self.raw_text.set(directory)

    def delete(self):
        for widget in [self.summary_label, self.summary_directory,
                       self.summary_chooser, self.raw_label,
                       self.raw_directory, self.raw_chooser]:
            widget.grid_forget()
            widget.destroy()

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
        print('here')
        self.x_statistic = new_value
        if (self.x_statistic == 'channel'):
            self.counts, self.bins, self.bars = self.ax.hist(self.data[self.x_statistic], edgecolor='black', bins=512)
        else:
            self.counts, self.bins, self.bars = self.ax.hist(self.data[self.x_statistic], edgecolor='black', bins=20)

        self.data_label = self.ax.text(0.8, 0.8, self.x_statistic + ': ', verticalalignment='center',
                                          horizontalalignment='center', transform=self.ax.transAxes)
        self.fig.canvas.draw()

class GraphWindow(tk.Toplevel):
    def __init__(self, parent, df_runs, raw_data, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.xaxis = 'mean'
        self.yaxis = 'stdv'
        varX = tk.StringVar()
        varX.set(self.xaxis)
        varY = tk.StringVar()
        varY.set(self.yaxis)
        options = {'mean', 'stdv', 'median', 'max', 'min'}
        self.layout = tk.PanedWindow(self, sashpad=4, sashrelief=tk.RAISED)
        self.control_panel = tk.Frame(self.layout, width=20)
        self.graph = tk.Frame(self.layout)

        self.xAxisSelect = tk.OptionMenu(self.control_panel, varX, *options, command=self.update_x_axis)
        self.yAxisSelect = tk.OptionMenu(self.control_panel, varY, *options, command=self.update_y_axis)
        self.clearSelected_button = tk.Button(self.control_panel, text='Unselect all', width=15, command=self.clear_selected)
        self.showRawData_button = tk.Button(self.control_panel, text='Show Raw Data', width=15, command=self.showRawData)
        self.deleteButton = tk.Button(self.control_panel, text='Delete Channel', width=15, command=self.delete_channel)
        self.undoButton = tk.Button(self.control_panel, text='Undo Last Deletion', width=15, command=self.undo_delete)
        self.deleteChannel = tk.Entry(self.control_panel)
        self.isBox = tk.IntVar()
        self.box_select_on = tk.Checkbutton(self.control_panel, text='Box Select', variable=self.isBox, command=self.activate_box)
        self.deleteUnselected = tk.Button(self.control_panel, text='Clear Unselected', width=15, command=self.delete_unselected)
        self.showHistogram_button = tk.Button(self.control_panel, text='Show Histogram', width=15, command=self.show_histogram)
        self.export_data_button = tk.Button(self.control_panel, text='Export Data', width=15, command=self.export_data)
        self.export_path = tk.Entry(self.control_panel)

        self.export_description = tk.Label(self.control_panel, text="Path to export to (including name)")

        self.deleteButton.pack()
        self.deleteChannel.pack()
        self.undoButton.pack()
        self.xAxisSelect.pack()
        self.yAxisSelect.pack()
        self.showRawData_button.pack()
        self.clearSelected_button.pack()
        self.box_select_on.pack()
        self.deleteUnselected.pack()
        self.showHistogram_button.pack()
        self.export_description.pack()
        self.export_path.pack()
        self.export_data_button.pack()





        self.layout.add(self.control_panel)
        self.layout.add(self.graph)
        self.layout.paneconfigure(self.control_panel, sticky='nw')
        self.layout.paneconfigure(self.graph, sticky='nse')
        self.layout.pack(fill='both', expand=True)

        self.previousDataSets = []
        self.testSelectPoints = set()
        self.raw_data = raw_data
        self.runs = df_runs
        self.data = self.runs.groupby('channel')
        self.original_runs = self.runs

        self.fig,self.ax = plt.subplots()

        self.lines = []
        for channel, group in self.data:
            line, = self.ax.plot(group[self.xaxis], group[self.yaxis], 'o', ms=3, alpha=.3, picker=2, label=channel)
            self.lines.append(line)
        self.ax.set_xlabel(self.xaxis)
        self.ax.set_ylabel(self.yaxis)
        canvas = FigureCanvasTkAgg(self.fig, self.graph)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill = 'both', expand = True)
        toolbar = NavigationToolbar2Tk(canvas, self.graph)
        toolbar.update()
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        xs = [self.runs.iloc[data][self.xaxis] for data in self.testSelectPoints]
        ys = [self.runs.iloc[data][self.yaxis] for data in self.testSelectPoints]
        self.selected, = self.ax.plot(xs, ys, 'o', ms=10, alpha=.8, color='red', visible=False)

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

    def update_annot(self, dataind, line):
        channel = int(line.get_label())
        currData = self.data.get_group(channel).iloc[dataind["ind"][0]]
        newPoint = int(currData.name)
        text = "channel: " + str(channel) + ", index: " + str(newPoint)

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
                    self.testSelectPoints.add(index)
            self.update()

    def delete_channel(self):
        to_delete = [int(name.strip()) for name in self.deleteChannel.get().split(',')]
        for name in to_delete:
            if name in self.data.groups:
                oldData = self.data
                oldRuns = self.runs
                self.runs = self.data.filter(lambda x : x.name != name)
                self.data = self.runs.groupby('channel')
                self.previousDataSets.append((oldData, oldRuns))
        self.update_lines()

    def delete_unselected(self):
        oldRuns = self.runs
        oldData = self.data
        for index, row in self.runs.iterrows():
            if int(row.name) not in self.testSelectPoints:
                self.runs = self.runs.drop(index)
        self.data = self.runs.groupby('channel')
        self.previousDataSets.append((oldData, oldRuns))
        self.update_lines()
        print('done')


    def undo_delete(self):
        if self.previousDataSets:
            oldData, oldRuns = self.previousDataSets.pop()
            self.runs = oldRuns
            self.data = oldData
        self.update_lines()

    def clear_selected(self):
        self.testSelectPoints.clear()
        self.update()

    def showRawData(self):
        if self.testSelectPoints:
            indices = list(self.testSelectPoints)
            self.rawDataWindow = RawDataWindow(self, self.raw_data, indices)

    def onpick(self, event):
        if event.artist not in self.lines:
            return True
        N = len(event.ind)
        if not N:
            return True

        channel = int(event.artist.get_label())
        dataind = event.ind[0]
        currData = self.data.get_group(channel).iloc[dataind]
        newPoint = int(currData.name)
        if newPoint in self.testSelectPoints:
            self.testSelectPoints.remove(newPoint)
        else:
            self.testSelectPoints.add(newPoint)
        self.update()

    def update_lines(self):
        for line in self.lines:
            channel = int(line.get_label())
            if channel in self.data.groups:
                currGroup = self.data.get_group(channel)
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

    def update(self):
        self.selected.set_visible(True)
        xs = [self.original_runs.iloc[data][self.xaxis] for data in self.testSelectPoints]
        ys = [self.original_runs.iloc[data][self.yaxis] for data in self.testSelectPoints]
        self.selected.set_data(xs, ys)
        self.fig.canvas.draw()



class RawDataWindow(tk.Toplevel):

    def __init__(self, parent, raw_data, indices, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.raw_data = raw_data

        self.hideFromScatter = tk.Button(self, text='Hide from Scatter', width=15, command=self.removeDataFromParent)
        self.showOnScatter = tk.Button(self, text='Show on Scatter', width=15, command=self.addDataToParent)
        self.hideFromScatter.pack()
        self.showOnScatter.pack()

        self.fig, self.ax = plt.subplots(2)
        self.rawLines = {}
        self.logLines = {}
        for index in indices:
            rawLine = self.ax[0].plot(raw_data[index], picker=True, label=index)
            logLine = self.ax[1].semilogx(raw_data[index], picker=True, label=index)
            self.rawLines[index] = rawLine
            self.logLines[index] = logLine
        self.ax[0].legend(indices)
        self.ax[0].set_title('Raw Data')
        self.ax[1].set_title('Log scaled')
        plt.subplots_adjust(hspace=0.4)
        canvas = FigureCanvasTkAgg(self.fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        self.fig.canvas.mpl_connect('pick_event', self.onpick)

    def onpick(self, event):
        index = int(event.artist.get_label())
        if index not in self.rawLines.keys():
            return True
        N = len(event.ind)
        if not N:
            return True

        todeleteRaw = self.rawLines[index][0]
        todeleteLog = self.logLines[index][0]
        self.rawLines.pop(index, None)
        self.logLines.pop(index, None)
        todeleteRaw.remove()
        todeleteLog.remove()
        self.parent.testSelectPoints.remove(index)
        self.parent.update()
        self.fig.canvas.draw()
        self.update_axes()

    def addDataToParent(self):
        for index in self.rawLines.keys():
            self.parent.testSelectPoints.add(index)
        self.parent.update()

    def removeDataFromParent(self):
        for index in self.rawLines.keys():
            if index in self.parent.testSelectPoints:
                self.parent.testSelectPoints.remove(index)
        self.parent.update()

    def update_axes(self):
        max_y = max([max(self.raw_data[index]) for index in self.rawLines])
        max_x = max([len(self.raw_data[index]) for index in self.rawLines])
        min_x = 0
        min_y = min([min(self.raw_data[index]) for index in self.rawLines])
        x_dif = (max_x - min_x) / 10
        y_dif = (max_y - min_y) / 10
        self.ax[0].set_xlim(min_x - x_dif, max_x + x_dif)
        self.ax[0].set_ylim(min_y - y_dif, max_y + y_dif)
        self.fig.canvas.draw()



def proper_exit():
    root.quit()
    root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', proper_exit)
    ControlPanel(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
