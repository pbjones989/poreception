import tkinter as tk
from control_panel import ControlPanel

def proper_exit():
    root.quit()
    root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', proper_exit)
    ControlPanel(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
