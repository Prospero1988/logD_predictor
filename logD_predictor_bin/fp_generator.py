# fp_generator.py

import os
import sys
import pandas as pd
from rdkit import Chem
from rdkit import DataStructs

# ANSI color codes for console output
COLORS = ['\033[38;5;46m',    # Green
          '\033[38;5;196m',   # Red
          '\033[38;5;214m'    # Orange
         ]
RESET = '\033[0m'


def fp_generator(csv_path, quiet=False):
    """
    Generates .csv files containing fingerprints from SMILES strings provided in a CSV file.

    Each output CSV file is named according to the 'MOLECULE_NAME' value and contains
    a single column with the fingerprint bits. No headers or indexes are included in the output files.

    Parameters:
    - csv_path (str): Path to the input CSV file containing 'MOLECULE_NAME' and 'SMILES' columns.

    Returns:
    - fp_directory (str): Path to the directory where generated fingerprint CSV files are stored.
    """
    # Definiowanie funkcji kontrolującej drukowanie
    def verbose_print(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    fp_directory = os.path.join(os.getcwd(), "fp")

    if not os.path.exists(fp_directory):
        os.makedirs(fp_directory)
        verbose_print(f"\nCreated directory: {COLORS[2]}{fp_directory}{RESET}")

    try:
        data = pd.read_csv(csv_path)
        if 'MOLECULE_NAME' not in data.columns or 'SMILES' not in data.columns:
            raise ValueError(f"{COLORS[1]}CSV must contain 'MOLECULE_NAME' and 'SMILES' columns.{RESET}")

        # Removing duplicates in the 'MOLECULE_NAME' column
        initial_count = len(data)
        data = data.drop_duplicates(subset='MOLECULE_NAME', keep='first')
        duplicates_count = initial_count - len(data)
        if duplicates_count > 0:
            verbose_print(f"{COLORS[1]}\nRemoved {duplicates_count} duplicates in 'MOLECULE_NAME'.{RESET}")

        file_count = 0        # Counter for successfully generated fingerprint files
        error_file_count = 0  # Counter for fingerprint files with errors

        print("\nGenerating fingerprint files ...\n")

        total_files = len(data)
        last_update = 0  # Last progress percentage update

        for index, row in enumerate(data.iterrows(), 1):
            try:
                name = row[1]['MOLECULE_NAME']
                smiles = row[1]['SMILES']
                
                # Convert SMILES string to RDKit molecule object
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    raise ValueError(f"Invalid SMILES string: {smiles}")

                # Generate fingerprint directly from molecule object
                fingerprint = Chem.RDKFingerprint(mol)

                # Convert fingerprint to list of bits (integers 0 or 1)
                fp_array = list(fingerprint.ToBitString())

                # Create a DataFrame from the list
                df_fp = pd.DataFrame(fp_array)

                # Optionally transpose the DataFrame if bits are in a row
                # df_fp = df_fp.T

                # Save DataFrame to CSV file without headers and index
                fp_file_path = os.path.join(fp_directory, f"{name}.csv")
                df_fp.to_csv(fp_file_path, header=False, index=False)

                file_count += 1  # Increment counter for successful files

            except Exception as e:
                error_file_count += 1  # Increment counter for error files
                error_file_path = os.path.join(fp_directory, f"{name}_error.txt")
                with open(error_file_path, 'w') as f:
                    f.write(f"Error processing {name}: {e}")

            # Update progress bar if progress increased by at least 1%
            progress = (index / total_files) * 100
            if progress - last_update >= 1 or index == total_files:
                print_progress(index, total_files)
                last_update = progress

        verbose_print(f"\n{COLORS[0]}Generated {file_count} fingerprint CSV files in the folder {COLORS[2]}'{fp_directory}'.{RESET}")
        verbose_print(f"{COLORS[0]}Encountered {error_file_count} errors during fingerprint generation.{RESET}")

    except FileNotFoundError:
        print(f"{COLORS[1]}File not found: {csv_path}{RESET}")
    except pd.errors.EmptyDataError:
        print(f"{COLORS[1]}File is empty: {csv_path}{RESET}")
    except pd.errors.ParserError:
        print(f"{COLORS[1]}Error parsing CSV file: {csv_path}{RESET}")
    except Exception as e:
        print(f"{COLORS[1]}An unexpected error occurred: {e}{RESET}")

    return fp_directory


def print_progress(current, total):
    """
    Prints a dynamic progress bar with color to indicate progress.

    Parameters:
    - current (int): The current file being processed.
    - total (int): The total number of files to process.
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
