import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import sys
import os
import webbrowser  # Import webbrowser to open URLs

# Tooltip class
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffff", relief='solid', borderwidth=1,
                         font=("Arial", 10, "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def run_script():
    csv_path = csv_path_var.get()
    if not csv_path:
        messagebox.showwarning("File Missing", "Please select a CSV file.")
        return

    predictor = predictor_var.get()
    args = [sys.executable, "logD_predictor.py", csv_path, f"--predictor={predictor}"]

    if debug_var.get():
        args.append("--debug")
    if models_var.get():
        args.append("--models")
    if quiet_var.get():
        args.append("--quiet")
    if chart_var.get():
        args.append("--chart")
    if use_svr_var.get():
        args.append("--use_svr")
    if use_xgb_var.get():
        args.append("--use_xgb")
    if use_dnn_var.get():
        args.append("--use_dnn")
    if use_cnn_var.get():
        args.append("--use_cnn")

    # Run the script in a new terminal window
    if sys.platform == "win32":
        subprocess.Popen(["start", "cmd", "/K"] + args, shell=True)
    else:
        subprocess.Popen(["x-terminal-emulator", "-e"] + args)

def select_csv():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        csv_path_var.set(filepath)

def open_example_file():
    example_file_path = os.path.join(os.getcwd(), "input_example.csv")
    try:
        if sys.platform == "win32":
            os.startfile(example_file_path)
        else:
            subprocess.Popen(["open", example_file_path] if sys.platform == "darwin" else ["xdg-open", example_file_path])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open the file: {e}")

def load_example_as_input():
    example_file_path = os.path.join(os.getcwd(), "input_example.csv")
    if os.path.exists(example_file_path):
        csv_path_var.set(example_file_path)
    else:
        messagebox.showerror("Error", "Example file not found.")

def open_help():
    # Open the GitHub repository in the default web browser
    webbrowser.open("https://github.com/Prospero1988/logD_predictor")

# Initialize GUI
root = tk.Tk()
root.title("logD Predictor GUI")

# Logo
path_to_logo = os.path.join(os.getcwd(), "IMG", "LOGO.png")
try:
    logo_img = Image.open(path_to_logo)
    logo_img = logo_img.resize((300, 100), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(root, image=logo_photo)
    logo_label.image = logo_photo
    logo_label.grid(row=0, column=0, columnspan=2, pady=10)
except Exception as e:
    print("Error loading logo:", e)

# CSV file path
csv_path_var = tk.StringVar()
tk.Label(root, text="SELECT .CSV INPUT FILE:").grid(row=1, column=0, columnspan=2, pady=5)
tk.Entry(root, textvariable=csv_path_var, width=50).grid(row=2, column=0, columnspan=2)

select_file_button = tk.Button(root, text="Select File", command=select_csv)
select_file_button.grid(row=3, column=0, columnspan=2, pady=5)

# Example buttons
example_frame = tk.Frame(root)
example_frame.grid(row=4, column=0, columnspan=2, pady=20)

example_button = tk.Button(example_frame, text="Open Input File Example", command=open_example_file)
example_button.grid(row=0, column=0, padx=5)

load_example_button = tk.Button(example_frame, text="Start with Input Example", command=load_example_as_input)
load_example_button.grid(row=0, column=1, padx=5)

help_button = tk.Button(example_frame, text="Open Help", command=open_help)
help_button.grid(row=0, column=2, padx=5)

# Expanding frames
def toggle_section(section_frame, section_button, expanded_text, collapsed_text):
    if section_frame.winfo_ismapped():
        section_frame.grid_remove()
        section_button.config(text=collapsed_text)
    else:
        section_frame.grid()
        section_button.config(text=expanded_text)
    root.update_idletasks()
    root.geometry('')

# SELECT REPRESENTATION
representation_button = tk.Button(root, text="SELECT REPRESENTATION [-]",
                                  command=lambda: toggle_section(representation_frame, representation_button, 
                                                                 "SELECT REPRESENTATION [-]", "SELECT REPRESENTATION [+]"))
representation_button.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=5)

representation_frame = tk.Frame(root)
representation_frame.grid(row=6, column=0, columnspan=2, padx=10, sticky="w")
#representation_frame.grid_remove()

predictor_var = tk.StringVar(value="all")
predictor_options = {
    "1H": "Proton (1H) NMR",
    "13C": "Carbon (13C) NMR",
    "FP": "RDKit Fingerprints",
    "all": "All Above"
}

for value, alias in predictor_options.items():
    tk.Radiobutton(representation_frame, text=alias, variable=predictor_var, value=value).pack(anchor="w")

# AVAILABLE MODELS
available_models_button = tk.Button(root, text="AVAILABLE MODELS [+]",
                                    command=lambda: toggle_section(models_frame, available_models_button,
                                                                   "AVAILABLE MODELS [-]", "AVAILABLE MODELS [+]"))
available_models_button.grid(row=7, column=0, columnspan=2, sticky="w", padx=10, pady=5)

models_frame = tk.Frame(root)
models_frame.grid(row=8, column=0, columnspan=2, padx=10, sticky="w")
models_frame.grid_remove()

use_svr_var = tk.BooleanVar(value=True)
use_xgb_var = tk.BooleanVar(value=True)
use_dnn_var = tk.BooleanVar(value=True)
use_cnn_var = tk.BooleanVar(value=True)

tk.Checkbutton(models_frame, text="Enable SVR", variable=use_svr_var).pack(anchor="w")
tk.Checkbutton(models_frame, text="Enable XGB", variable=use_xgb_var).pack(anchor="w")
tk.Checkbutton(models_frame, text="Enable DNN", variable=use_dnn_var).pack(anchor="w")
tk.Checkbutton(models_frame, text="Enable CNN", variable=use_cnn_var).pack(anchor="w")

# SCRIPT EXECUTION OPTIONS
script_options_button = tk.Button(root, text="SCRIPT EXECUTION OPTIONS [+]",
                                  command=lambda: toggle_section(script_options_frame, script_options_button,
                                                                 "SCRIPT EXECUTION OPTIONS [-]", "SCRIPT EXECUTION OPTIONS [+]"))
script_options_button.grid(row=9, column=0, columnspan=2, sticky="w", padx=10, pady=5)

script_options_frame = tk.Frame(root)
script_options_frame.grid(row=10, column=0, columnspan=2, padx=10, sticky="w")
script_options_frame.grid_remove()

debug_var = tk.BooleanVar()
models_var = tk.BooleanVar()
quiet_var = tk.BooleanVar(value=True)
chart_var = tk.BooleanVar(value=True)

tk.Checkbutton(script_options_frame, text="Debug mode", variable=debug_var).pack(anchor="w")
tk.Checkbutton(script_options_frame, text="Show models", variable=models_var).pack(anchor="w")
tk.Checkbutton(script_options_frame, text="Quiet mode", variable=quiet_var).pack(anchor="w")
tk.Checkbutton(script_options_frame, text="Generate charts", variable=chart_var).pack(anchor="w")

# Run script button
tk.Button(root, text="PREDICT!", command=run_script, font=("Arial", 10, "bold")).grid(row=11, column=0, columnspan=2, pady=20)

root.mainloop()
