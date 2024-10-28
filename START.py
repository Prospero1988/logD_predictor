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
root.geometry("400x580")  # Adjusted window height to fit logo

path_to_logo = os.path.join(os.getcwd(), "IMG", "LOGO.png")
# Load and display the logo image
try:
    logo_img = Image.open(path_to_logo)  # Replace with your logo path
    logo_img = logo_img.resize((300, 100), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(root, image=logo_photo)
    logo_label.image = logo_photo  # Keep a reference to avoid garbage collection
    logo_label.pack(pady=10)
except Exception as e:
    print("Error loading logo:", e)

# CSV file path
csv_path_var = tk.StringVar()
tk.Label(root, text="SELECT .CSV INPUT FILE:").pack(pady=5, anchor="center")
tk.Entry(root, textvariable=csv_path_var, width=50).pack()

# Define the Select File button
select_file_button = tk.Button(root, text="Select File", command=select_csv)
select_file_button.pack(pady=5)

# Frame for example buttons, centered in the main window, with a fixed 10-pixel padding
example_frame = tk.Frame(root)
example_frame.pack(anchor="center", pady=20)  # Offset by a fixed 10 pixels

# Buttons with even padding in between
example_button = tk.Button(example_frame, text="Input File Example", command=open_example_file)
example_button.pack(side="left", padx=(5, 5))

load_example_button = tk.Button(example_frame, text="Start with Input Example", command=load_example_as_input)
load_example_button.pack(side="left", padx=(5, 5))

help_button = tk.Button(example_frame, text="Open Help", command=open_help)
help_button.pack(side="left", padx=(5, 5))

# Predictor selection with aliases
tk.Label(root, text="SELECT PREDICTOR MODEL:").pack(pady=5, anchor="center")
predictor_var = tk.StringVar(value="all")

# Define options and aliases
predictor_options = {
    "1H": "Proton (1H) NMR",
    "13C": "Carbon (13C) NMR",
    "FP": "Fingerprint (FP) Analysis",
    "all": "All Predictors"
}

# Create radio buttons with aliases as display text
for value, alias in predictor_options.items():
    tk.Radiobutton(root, text=alias, variable=predictor_var, value=value).pack(anchor="w")

# Script execution options
tk.Label(root, text="SCRIPT EXECUTION OPTIONS:").pack(pady=5, anchor="center")
debug_var = tk.BooleanVar()
models_var = tk.BooleanVar()
quiet_var = tk.BooleanVar(value=True)  # Set quiet mode to be checked by default

# Checkbuttons with tooltip
debug_button = tk.Checkbutton(root, text="Debug mode", variable=debug_var)
debug_button.pack(anchor="w")
ToolTip(debug_button, "Enable debug mode for additional logging. Use it to save all temporary files.")

models_button = tk.Checkbutton(root, text="Show models", variable=models_var)
models_button.pack(anchor="w")
ToolTip(models_button, "Display Machine Learning model details in the output.")

quiet_button = tk.Checkbutton(root, text="Quiet mode", variable=quiet_var)
quiet_button.pack(anchor="w")
ToolTip(quiet_button, "Suppress non-essential output messages. Default option.")

# Button to run the script
tk.Button(root, text="START Predictions", command=run_script).pack(pady=20)

root.mainloop()
