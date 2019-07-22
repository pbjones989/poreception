import sys
import time
import os
import tkinter as tk
from tkinter import messagebox
import numpy as np
import h5py
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from tkinter.filedialog import askopenfilename
from matplotlib.widgets import RectangleSelector
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from h5_menu_options import H5MenuOptions
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
            summary_data = {'run':[], 'channel':[], 'start_obs':[],
                            'end_obs':[], 'duration_obs':[], 'mean':[], 
                            'stdv':[], 'median':[], 'min':[], 'max':[], 
                            'open_channel':[]}
            raw_data = []
            for menu_option in self.data_sets:
                if os.path.exists(menu_option.h5_directory):
                    for multi_fast5_path in os.listdir(menu_option.h5_directory):
                        multi_fast5_path = os.path.join(menu_option.h5_directory, multi_fast5_path)
                        multi_fast5 = h5py.File(multi_fast5_path, 'r')
                        self.add_multi_fast5(multi_fast5, summary_data, raw_data)
                
            summary_df = pd.DataFrame(data=summary_data)
            summary_df = summary_df.reset_index(drop=True)
            GraphWindow(self, summary_df, np.array(raw_data))                

    def add_multi_fast5(self, multi_fast5, summary_data, raw_data):
        for read_name in multi_fast5.keys():
            read = multi_fast5[read_name]
            read_raw_data = read['Raw']
            channel_info = read['channel_id']

            summary_data['run'].append(read.attrs['run_id'])
            summary_data['channel'].append(channel_info.attrs['channel_number'])
            summary_data['start_obs'].append(read_raw_data.attrs['start_obs'])
            summary_data['end_obs'].append(read_raw_data.attrs['end_obs'])
            summary_data['duration_obs'].append(read_raw_data.attrs['duration_obs'])
            summary_data['mean'].append(read_raw_data.attrs['mean'])
            summary_data['stdv'].append(read_raw_data.attrs['stdv'])
            summary_data['median'].append(read_raw_data.attrs['median'])
            summary_data['min'].append(read_raw_data.attrs['min'])
            summary_data['max'].append(read_raw_data.attrs['max'])
            summary_data['open_channel'].append(channel_info.attrs['open_channel_current'])

            raw_data.append(read_raw_data['Signal'][()])

    def add_data_set(self):
        new_menu_option = H5MenuOptions(self)
        new_menu_option.grid(row=self.data_row, columnspan=3)
        self.data_row += 1
        self.data_sets.append(new_menu_option)

    def remove_data_set(self):
        if self.data_sets:
            old_menu_option = self.data_sets.pop()
            old_menu_option.grid_forget()
            old_menu_option.destroy()
            self.data_row -= 1
