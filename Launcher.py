import tkinter as tk
from tkinter import ttk
import time
import sys
import subprocess

class SplashScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        width = 500
        height = 300
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.config(bg="#030005")

        tk.Label(self.root, text="SEMATEC LMS", font=("Segoe UI Black", 28), bg="#030005", fg="white").pack(
            pady=(70, 10))
        tk.Label(self.root, text="Loading System Modules & Database...", font=("Segoe UI", 10), bg="#030005",
                 fg="#dcdde1").pack()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Purple.Horizontal.TProgressbar", foreground='#520034', background='#520034')
        self.progress = ttk.Progressbar(self.root, style="Purple.Horizontal.TProgressbar", orient=tk.HORIZONTAL,
                                        length=400, mode='determinate')
        self.progress.pack(pady=(40, 0))
        self.root.after(50, self.load_system)
        self.root.mainloop()

    def load_system(self):
        for i in range(101):
            time.sleep(0.015)
            self.progress['value'] = i
            self.root.update_idletasks()
        self.root.destroy()

        subprocess.Popen([sys.executable, "LoginModule.py"])

if __name__ == "__main__":
    SplashScreen()