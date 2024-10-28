import subprocess
import sys

# List of modules to check and install if necessary with specified versions
modules = [
    ('tqdm', 'tqdm'),
    ('pandas', 'pandas'),
    ('art', 'art'),
    ('numpy', 'numpy==1.24.4'),
    ('rdkit', 'rdkit'),
    ('scikit-learn', 'scikit-learn==1.3.2'),
    ('xgboost', 'xgboost==2.1.1'),
    ('PILLOW', 'pillow')
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
try:
    from tqdm import tqdm
    import pandas as pd
    import art
    import numpy as np
    from rdkit import Chem
    import sklearn
    import xgboost as xgb
    print("\nAll required modules are installed and successfully imported.\n")
except ImportError as e:
    print(f"Error importing modules: {e}")

input("Press ENTER to exit: ")
