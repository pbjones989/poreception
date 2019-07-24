import sys
import os
import tkinter as tk
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from tkinter.filedialog import askdirectory
from matplotlib.widgets import RectangleSelector
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class H5MenuOptions(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.h5_label = tk.Label(self, text='Multifast5 folder:', font='TkDefaultFont 13 bold')
        self.h5_text = tk.StringVar()
        self.h5_directory = tk.Label(self, textvariable=self.h5_text)
        self.h5_chooser = tk.Button(self, text='Choose HFD5 Folder', command=self.choose_h5_data)

        self.h5_label.grid(row=0, column=0)
        self.h5_directory.grid(row=0, column=1)
        self.h5_chooser.grid(row=0, column=2)

        self.h5_directory = ""

    def choose_h5_data(self):
        self.h5_directory = askdirectory(initialdir=os.getcwd())
        self.h5_text.set(self.h5_directory)

    def delete(self):
        for widget in [self.h5_label, self.h5_directory,
                       self.h5_chooser]:
            widget.grid_forget()
            widget.destroy()
