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
from menu_options import MenuOptions
from graph_window import GraphWindow

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
