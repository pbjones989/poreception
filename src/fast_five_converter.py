import os
import h5py
import tkinter as tk
import numpy as np
from tkinter import messagebox
from menu_options import MenuOptions

class ConvertPanel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.root = parent
        self.root.title("Fast Five Converter")

        files_label = tk.Label(self, text='pkl and npy files of summary/raw data for a run:', font='TkDefaultFont 13 bold')
        self.files = MenuOptions(self)
        name_label = tk.Label(self, text='hdf5 file name: (will append .hdf5 to what is given)', font='TkDefaultFont 13 bold')
        self.file_name = tk.Entry(self)
        export_button = tk.Button(self, text='Create hdf5 file', command=self.export_data)
        files_label.grid(row=0, column=0, sticky='EW')
        self.files.grid(row=1, column=0, columnspan=2, sticky='EW')
        name_label.grid(row=2, column=0, sticky='EW')
        self.file_name.grid(row=2, column=1, sticky='EW')
        export_button.grid(row=3, column=0, sticky='SEW')

    def export_data(self):
        if os.path.exists(self.files.summary_directory) and os.path.exists(self.files.raw_directory):
            summary_data = np.load(self.files.summary_directory, encoding = 'latin1')
            if isinstance(summary_data['channel'][0], str):
                summary_data['channel'] = summary_data['channel'].map(lambda s: int(s[8:]))
            raw_data = np.load(self.files.raw_directory, encoding = 'latin1')
            new_file_name = self.file_name.get() + ".hdf5"
            summary_data.to_hdf(new_file_name, key="summary", mode="w")
            new_file = h5py.File(new_file_name, "a")
            new_grp = new_file.create_group('raw')
            i = 0
            for data_set in raw_data:
                new_grp.create_dataset(str(i), data=data_set.astype(np.float64))
                i += 1
        else:
            messagebox.showinfo("No File Found",
                    "Could not find data files\n    given summary: "
                    + self.files.summary_directory +
                    "\n    given raw: " + self.files.raw_directory)
            return




def proper_exit():
    root.quit()
    root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', proper_exit)
    ConvertPanel(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
