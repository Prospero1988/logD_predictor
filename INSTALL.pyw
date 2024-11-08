import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import os
import sys
import subprocess
import webbrowser

# Ensure we use python.exe instead of pythonw.exe
if sys.executable.endswith('pythonw.exe'):
    python_executable = sys.executable.replace('pythonw.exe', 'python.exe')
else:
    python_executable = sys.executable

# Path setup
install_script_path = os.path.join(os.getcwd(), "logD_predictor_bin", "install_modules.py")
info_text_path = os.path.join(os.getcwd(), "logD_predictor_bin", "install_text.txt")
logo_path = os.path.join(os.getcwd(), "IMG", "LOGO.png")

# Initialize the root window
root = tk.Tk()
root.title("logD Predictor Installer")
root.resizable(True, True)  # Allow window resizing

# Add scrolled text for the license/information
info_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=38)
info_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

# Load text content from file
try:
    with open(info_text_path, "r") as file:
        info_text.insert(tk.END, file.read())
except FileNotFoundError:
    info_text.insert(tk.END, "Information file not found.")

# Define button actions
def run_install():

    command = [python_executable, install_script_path]

    if sys.platform == "win32":
        from subprocess import CREATE_NEW_CONSOLE
        # Use creationflags to open a new console window
        subprocess.Popen(command, creationflags=CREATE_NEW_CONSOLE, cwd=os.getcwd())
    elif sys.platform == "darwin":
        # For macOS
        subprocess.Popen(["open", "-a", "Terminal.app"] + command, cwd=os.getcwd())
    else:
        # For Linux
        subprocess.Popen(["x-terminal-emulator", "-e"] + command, cwd=os.getcwd())

    root.destroy()    

def open_help():
    webbrowser.open("https://github.com/Prospero1988/logD_predictor")

def cancel():
    root.destroy()

# Create buttons
help_button = tk.Button(root, text="HELP", command=open_help, font=("Arial", 10))
help_button.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 50))
help_button.bind("<Enter>", lambda e: help_button.config(tooltip="Click to open the repository page on Github in your browser, where you will find information about the program and help."))

cancel_button = tk.Button(root, text="CANCEL", command=cancel, font=("Arial", 10))
cancel_button.grid(row=3, column=0, sticky="w", padx=20, pady=20)
cancel_button.bind("<Enter>", lambda e: cancel_button.config(tooltip="Cancel operations and close program."))

install_button = tk.Button(root, text="INSTALL", command=run_install, font=("Arial", 10, "bold"))
install_button.grid(row=3, column=1, sticky="e", padx=20, pady=20)
install_button.bind("<Enter>", lambda e: install_button.config(tooltip="Click to install the required Python libraries to work with the logD_predictor software."))

# Run the GUI
root.mainloop()
