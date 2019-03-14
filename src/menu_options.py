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
