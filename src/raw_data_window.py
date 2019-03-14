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
