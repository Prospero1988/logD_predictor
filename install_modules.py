import os
import shutil
import re
import subprocess
import sys

# List of modules to check and install if necessary
modules = [
    ('tqdm', 'tqdm'),
    ('pandas', 'pandas'),
    ('art', 'art'),
    ('numpy', 'numpy'),
    ('rdkit', 'rdkit')
]

# Function to check and install a module
def check_and_install(module_name, package_name=None):
    try:
        __import__(module_name)
        print(f"Module {module_name} is already installed.")
    except ImportError:
        if package_name is None:
            package_name = module_name
        print(f"Installing module {module_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"Module {module_name} has been installed.")

# Check and install required modules
for module_name, package_name in modules:
    check_and_install(module_name, package_name)

# Importing verified modules
from tqdm import tqdm
import zipfile
import rarfile

print("\nAll required modules are installed.\n")
input("Press ENTER to exit: ")
