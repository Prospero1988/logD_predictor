import os
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
import sys
import time

# ANSI color
COLORS = ['\033[38;5;46m',    # Green
          '\033[38;5;196m',   # Red
          '\033[38;5;214m'    # Orange
         ]
RESET = '\033[0m'

def generate_mol_files(csv_path):
    """
    Generates .mol files from SMILES strings provided in a CSV file.

    Parameters:
    - csv_path (str): Path to the input CSV file containing 'MOLECULE_NAME'
                      and 'SMILES' columns.

    Returns:
    - mols_directory (str): Path to the directory where generated .mol files
                            are stored.
    """
    mols_directory = os.path.join(os.getcwd(), "mols")

    if not os.path.exists(mols_directory):
        os.makedirs(mols_directory)
        print(f"\nCreated directory: {COLORS[2]}{mols_directory}{RESET}")

    try:
        data = pd.read_csv(csv_path)
        if 'MOLECULE_NAME' not in data.columns or 'SMILES' not in data.columns:
            raise ValueError(f"{COLORS[1]}CSV must contain 'MOLECULE_NAME' and 'SMILES' columns.{RESET}")

        file_count = 0  # Counter for successfully generated .mol files
        error_file_count = 0  # Counter for .mol files with errors

        print("\nGenerating *.mol files ...\n")

        total_files = len(data)
        last_update = 0  # Last progress percentage update
        for index, row in enumerate(data.iterrows(), 1):
            try:
                name = row[1]['MOLECULE_NAME']
                smiles = row[1]['SMILES']
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    raise ValueError(f"{COLORS[1]}Invalid SMILES string: {smiles}{RESET}")

                mol = Chem.AddHs(mol)
                AllChem.EmbedMolecule(mol, randomSeed=0xf00d)
                AllChem.Compute2DCoords(mol)

                mol_file_path = os.path.join(mols_directory, f"{name}.mol")
                with open(mol_file_path, 'w') as f:
                    f.write(Chem.MolToMolBlock(mol, forceV3000=True))

                file_count += 1  # Increment counter for successful files

            except Exception as e:
                mol_file_path = os.path.join(mols_directory, f"{row[1]['MOLECULE_NAME']}_error.mol")
                with open(mol_file_path, 'w') as f:
                    if mol:
                        f.write(Chem.MolToMolBlock(mol, forceV3000=True))
                    else:
                        f.write(f"{COLORS[1]}{name} could not be processed due to an error: {e}{RESET}")
                error_file_count += 1  # Increment counter for error files

            # Only update progress every 1%
            progress = (index / total_files) * 100
            if progress - last_update >= 1:
                print_progress(index, total_files)
                last_update = progress

        # The line below has been removed to avoid displaying the progress bar twice
        # print_progress(total_files, total_files)

        print(f"\n{COLORS[0]}Generated {file_count} .mol files in the folder {COLORS[2]}'{mols_directory}'.{RESET}")
        print(f"{COLORS[0]}Generated {error_file_count} .mol files with errors (saved as *_error.mol).{RESET}")

    except FileNotFoundError:
        print(f"{COLORS[1]}File not found: {csv_path}{RESET}")
    except pd.errors.EmptyDataError:
        print(f"{COLORS[1]}File is empty: {csv_path}{RESET}")
    except pd.errors.ParserError:
        print(f"{COLORS[1]}Error parsing CSV file: {csv_path}{RESET}")
    except Exception as e:
        print(f"{COLORS[1]}An unexpected error occurred: {e}{RESET}")

    return mols_directory

def print_progress(current, total):
    """
    Prints a dynamic progress bar with color to indicate progress.

    Parameters:
    - current: the current file being processed
    - total: the total number of files to process
    """
    bar_length = 25  # Length of the progress bar
    filled_length = int(bar_length * (current / total))

    # Build the progress bar with colored blocks
    color_cycle = COLORS[0]
    bar = color_cycle + '█' * filled_length + '-' * (bar_length - filled_length) + RESET

    percent = int(100 * current / total)

    sys.stdout.write(f"\rProgress: |{bar}| {current}/{total} ({percent}%)")
    sys.stdout.flush()

    if current == total:
        print('')  # Add a newline after the last update
