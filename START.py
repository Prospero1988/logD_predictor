import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys

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

# Initialize GUI
root = tk.Tk()
root.title("logD Predictor GUI")
root.geometry("400x400")  # Adjusted window height

# CSV file path
csv_path_var = tk.StringVar()
tk.Label(root, text="Path to CSV file:").pack(pady=5, anchor="w")
tk.Entry(root, textvariable=csv_path_var, width=50).pack()
tk.Button(root, text="Select File", command=select_csv).pack(pady=5)

# Predictor selection
tk.Label(root, text="Select predictor:").pack(pady=5, anchor="w")
predictor_var = tk.StringVar(value="all")
predictor_options = ["1H", "13C", "FP", "all"]
for option in predictor_options:
    tk.Radiobutton(root, text=option, variable=predictor_var, value=option).pack(anchor="w")

# Script execution options
tk.Label(root, text="Script execution options:").pack(pady=5, anchor="w")
debug_var = tk.BooleanVar()
models_var = tk.BooleanVar()
quiet_var = tk.BooleanVar()
tk.Checkbutton(root, text="Debug mode", variable=debug_var).pack(anchor="w")
tk.Checkbutton(root, text="Show models", variable=models_var).pack(anchor="w")
tk.Checkbutton(root, text="Quiet mode", variable=quiet_var).pack(anchor="w")

# Button to run the script
tk.Button(root, text="Run Script", command=run_script).pack(pady=20)

root.mainloop()
