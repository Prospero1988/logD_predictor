import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import sys
import os
import webbrowser

class ToolTip:
    """
    Tooltip for a given widget.
    Displays a small popup with helpful text when hovering over the widget.
    """
    def __init__(self, widget, text):
        """
        Initialize the tooltip.

        Args:
            widget: The Tkinter widget to attach the tooltip to.
            text: The text to display in the tooltip.
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """
        Show the tooltip window near the widget.
        """
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify='left',
            background="#ffffff",
            relief='solid',
            borderwidth=1,
            font=("Arial", 10, "normal")
        )
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        """
        Hide the tooltip window if it is visible.
        """
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def run_script():
    """
    Run the logD predictor script with the selected options.
    """
    csv_path = csv_path_var.get()
    if not csv_path:
        messagebox.showwarning("File Missing", "Please select a CSV file.")
        return

    predictor = predictor_var.get()

    # Use python.exe instead of pythonw.exe if needed
    if sys.executable.endswith('pythonw.exe'):
        python_executable = sys.executable.replace('pythonw.exe', 'python.exe')
    else:
        python_executable = sys.executable

    # Build the command as a list of arguments
    command = [
        python_executable,
        os.path.abspath(os.path.join(os.getcwd(), "logD_predictor_bin", "logD_predictor.py")),
        csv_path,
        f"--predictor={predictor}"
    ]

    # Add command-line flags based on user selections
    if debug_var.get():
        command.append('--debug')
    if models_var.get():
        command.append('--models')
    if quiet_var.get():
        command.append('--quiet')
    if chart_var.get():
        command.append('--chart')
    if use_svr_var.get():
        command.append('--use_svr')
    if use_xgb_var.get():
        command.append('--use_xgb')
    if use_dnn_var.get():
        command.append('--use_dnn')
    if use_cnn_var.get():
        command.append('--use_cnn')

    # Launch the script in a new terminal window
    if sys.platform == "win32":
        from subprocess import CREATE_NEW_CONSOLE
        subprocess.Popen(command, creationflags=CREATE_NEW_CONSOLE, cwd=os.getcwd())
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-a", "Terminal.app"] + command, cwd=os.getcwd())
    else:
        subprocess.Popen(["x-terminal-emulator", "-e"] + command, cwd=os.getcwd())

def select_csv():
    """
    Open a file dialog to select a CSV file and set its path.
    """
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        csv_path_var.set(filepath)

def open_example_file():
    """
    Open the example input CSV file using the default application.
    """
    example_file_path = os.path.join(os.getcwd(), "logD_predictor_bin", "input_example.csv")
    try:
        if sys.platform == "win32":
            os.startfile(example_file_path)
        else:
            subprocess.Popen(
                ["open", example_file_path] if sys.platform == "darwin" else ["xdg-open", example_file_path]
            )
    except Exception as e:
        messagebox.showerror("Error", f"Could not open the file: {e}")

def load_example_as_input():
    """
    Load the example input CSV file path into the input field.
    """
    example_file_path = os.path.join(os.getcwd(), "logD_predictor_bin", "input_example.csv")
    if os.path.exists(example_file_path):
        csv_path_var.set(example_file_path)
    else:
        messagebox.showerror("Error", "Example file not found.")

def open_help():
    """
    Open the GitHub repository page in the default web browser.
    """
    webbrowser.open("https://github.com/Prospero1988/logD_predictor")

def open_prediction_results():
    """
    Open the folder containing prediction results.
    """
    prediction_results_path = os.path.join(os.getcwd(), "Prediction_Results")
    try:
        if sys.platform == "win32":
            os.startfile(prediction_results_path)
        else:
            subprocess.Popen(
                ["xdg-open", prediction_results_path] if sys.platform != "darwin" else ["open", prediction_results_path]
            )
    except Exception as e:
        messagebox.showerror("Error", f"Could not open the folder: {e}")

def open_log():
    """
    Open the log file of the last prediction.
    """
    log_file_path = os.path.join(os.getcwd(), "RUN_LOG_FILE.log")
    try:
        if sys.platform == "win32":
            os.startfile(log_file_path)
        else:
            subprocess.Popen(
                ["open", log_file_path] if sys.platform == "darwin" else ["xdg-open", log_file_path]
            )
    except Exception as e:
        messagebox.showerror("Error", f"Could not open the file: {e}")

# Initialize GUI
root = tk.Tk()
root.title("logD Predictor GUI")

# Logo
path_to_logo = os.path.join(os.getcwd(), "logD_predictor_bin", "img", "LOGO.png")
try:
    logo_img = Image.open(path_to_logo)
    logo_img = logo_img.resize((300, 135), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(root, image=logo_photo)
    logo_label.image = logo_photo
    logo_label.grid(row=0, column=0, columnspan=2, pady=10, padx=20)
except Exception as e:
    print("Error loading logo:", e)

# CSV file path
csv_path_var = tk.StringVar()
tk.Label(root, text="SELECT .CSV INPUT FILE:").grid(row=2, column=0, columnspan=2, pady=5)
tk.Entry(root, textvariable=csv_path_var, width=50).grid(row=3, column=0, columnspan=2)

select_file_button = tk.Button(root, text="Select File", command=select_csv)
select_file_button.grid(row=4, column=0, columnspan=2, pady=5)
ToolTip(select_file_button, "Select a .csv file from disk containing \nthe names and structures of compounds \nin SMILES code form.")

# Example buttons
example_frame = tk.Frame(root)
example_frame.grid(row=5, column=0, columnspan=2, pady=20)

example_button = tk.Button(example_frame, text="Open Input File Example", command=open_example_file)
example_button.grid(row=0, column=0, padx=5)
ToolTip(example_button, "Opens an example input file that can be used \nas a starting point for predictions.")

load_example_button = tk.Button(example_frame, text="Start with Input Example", command=load_example_as_input)
load_example_button.grid(row=0, column=1, padx=5)
ToolTip(load_example_button, "Load the example input file to perform a test run \nfor predictions and familiarize yourself with the program.")

# New frame for “Open Help” and “Open Prediction Results” buttons.
action_frame = tk.Frame(root)
action_frame.grid(row=6, column=0, columnspan=2, pady=(5, 35))

open_results_button = tk.Button(action_frame, text="Open Results", command=open_prediction_results)
open_results_button.grid(row=0, column=0, padx=5)
ToolTip(open_results_button, "Open the directory containing prediction results.")

log_button = tk.Button(action_frame, text="Open LOG", command=open_log)
log_button.grid(row=0, column=1, padx=5)
ToolTip(log_button, "Opens a log file of the last prediction made. \nThe log file resets after each use of PREDICT!")

help_button = tk.Button(action_frame, text="Open Help", command=open_help)
help_button.grid(row=0, column=2, padx=5)
ToolTip(help_button, "Opens the program's GitHub repository page, \nwhere you can find installation instructions, \nusage, and other useful information.")

def toggle_section(section_frame, section_button, expanded_text, collapsed_text):
    """
    Expand or collapse a section in the GUI.

    Args:
        section_frame: The frame to show or hide.
        section_button: The button controlling the section.
        expanded_text: Text to display when expanded.
        collapsed_text: Text to display when collapsed.
    """
    if section_frame.winfo_ismapped():
        section_frame.grid_remove()
        section_button.config(text=collapsed_text)
    else:
        section_frame.grid()
        section_button.config(text=expanded_text)
    root.update_idletasks()
    root.geometry('')

# SELECT REPRESENTATION
representation_button = tk.Button(
    root,
    text="SELECT REPRESENTATION [-]",
    command=lambda: toggle_section(
        representation_frame,
        representation_button,
        "SELECT REPRESENTATION [-]",
        "SELECT REPRESENTATION [+]"
    )
)
representation_button.grid(row=7, column=0, columnspan=2, sticky="w", padx=10, pady=5)
ToolTip(
    representation_button,
    "Choose the type of representation that will be used\n"
    "for predicting logD parameters.\n"
    "Representation refers to the type of data\n"
    "used for training and querying the model."
)

representation_frame = tk.Frame(root)
representation_frame.grid(row=8, column=0, columnspan=2, padx=10, sticky="w")

predictor_var = tk.StringVar(value="all")
# Define options, aliases, and tooltips
predictor_options = {
    "hybrid": ("Hybrid ¹H | ¹³C", "Use hybrid representation combining ¹H and ¹³C NMR data."),
    "1H": ("Proton (¹H) NMR", "Use Proton (¹H) NMR data for predictions."),
    "13C": ("Carbon (¹³C) NMR", "Use Carbon (¹³C) NMR data for predictions."),
    "FP": ("RDKit Fingerprints", "Use RDKit Fingerprints for predictions."),
    }

# Create radio buttons with aliases and tooltips
for value, (alias, tooltip_text) in predictor_options.items():
    rb = tk.Radiobutton(representation_frame, text=alias, variable=predictor_var, value=value)
    rb.pack(anchor="w")
    ToolTip(rb, tooltip_text)

# AVAILABLE MODELS
available_models_button = tk.Button(
    root,
    text="AVAILABLE MODELS [+]",
    command=lambda: toggle_section(
        models_frame,
        available_models_button,
        "AVAILABLE MODELS [-]",
        "AVAILABLE MODELS [+]"
    )
)
available_models_button.grid(row=9, column=0, columnspan=2, sticky="w", padx=10, pady=5)
ToolTip(
    available_models_button,
    "Select the logD models you want to query.\n\n"
    "The more models you select, the more accurate the result\n"
    "due to a larger amount of data and the possibility\n"
    "of better averaging."
)

models_frame = tk.Frame(root)
models_frame.grid(row=10, column=0, columnspan=2, padx=10, sticky="w")
models_frame.grid_remove()

use_svr_var = tk.BooleanVar(value=True)
use_xgb_var = tk.BooleanVar(value=True)
use_dnn_var = tk.BooleanVar(value=True)
use_cnn_var = tk.BooleanVar(value=True)

model_options = [
    (use_svr_var, "Enable SVR", "Support Vector Regression Model optimized with Optuna."),
    (use_xgb_var, "Enable XGB", "Extreme Gradient Boosting Model optimized with Optuna."),
    (use_dnn_var, "Enable DNN", "Deep Neural Network Model optimized with Optuna."),
    (use_cnn_var, "Enable CNN", "Convolutional Neural Network Model optimized with Optuna.")
]

# Create checkbuttons with tooltips
for var, text, tooltip_text in model_options:
    cb = tk.Checkbutton(models_frame, text=text, variable=var)
    cb.pack(anchor="w")
    ToolTip(cb, tooltip_text)

# SCRIPT EXECUTION OPTIONS
script_options_button = tk.Button(
    root,
    text="SCRIPT EXECUTION OPTIONS [+]",
    command=lambda: toggle_section(
        script_options_frame,
        script_options_button,
        "SCRIPT EXECUTION OPTIONS [-]",
        "SCRIPT EXECUTION OPTIONS [+]"
    )
)
script_options_button.grid(row=11, column=0, columnspan=2, sticky="w", padx=10, pady=5)
ToolTip(
    script_options_button,
    "Additional options for the program.\n\n"
    "The default setup ensures clarity of operation.\n"
    "If you want to read individual values for the given models, \n"
    "not average values, uncheck the 'Quiet mode' option.\n"
    "'Debug mode' saves all files generated during the program's execution,\n"
    "including structures in mol files or NMR spectrum predictions.\n"
    "The 'Show models' option displays detailed information \n"
    "about the models at the end, such as their metrics and \n"
    "statistics like RMSE or MAE. \n"
    "'Generate charts' presents the obtained prediction values on a chart."
)

script_options_frame = tk.Frame(root)
script_options_frame.grid(row=12, column=0, columnspan=2, padx=10, sticky="w")
script_options_frame.grid_remove()

debug_var = tk.BooleanVar()
models_var = tk.BooleanVar()
quiet_var = tk.BooleanVar(value=True)
chart_var = tk.BooleanVar(value=True)

# Define script options and tooltips
script_options = [
    (debug_var, "Debug mode", "Enable debug mode for additional logging and save temporary files."),
    (models_var, "Show models", "Display Machine Learning model details in the output."),
    (quiet_var, "Quiet mode", "Suppress non-essential output messages. Enabled by default."),
    (chart_var, "Generate charts", "Generate charts with modeled logD values and standard deviation.")
]

# Create checkbuttons with tooltips
for var, text, tooltip_text in script_options:
    cb = tk.Checkbutton(script_options_frame, text=text, variable=var)
    cb.pack(anchor="w")
    ToolTip(cb, tooltip_text)

# Run script button
tk.Button(
    root,
    text="PREDICT!",
    command=run_script,
    font=("Arial", 10, "bold")
).grid(row=13, column=0, columnspan=2, pady=20)

root.mainloop()
