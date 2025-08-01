#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script Name: logD_predictor.py
Description: A script for predicting logD values using various machine learning models.
"""

import argparse
import shutil
import os
import subprocess
from art import text2art
import re
import sys

# Import custom modules required for the script
from csv_checker import verify_csv
from gen_mols import generate_mol_files
from predictor import run_java_batch_processor
from bucket import bucket
from merger import merger
from custom_header import custom_header
from model_query import query
from fp_generator import fp_generator
from concatenator import concatenate

def strip_ansi_codes(s):
    ansi_escape = re.compile(r'''
        \x1B # ESC
        (?:   # 7-bit C1 Fe (various sequences)
            [@-Z\\-_]
        | # or CSI [ - ].
            \[
            [0-?]* # Optional parameters.
            [-/]* # Optional intermediate bytes.
            [@-~] # Final byte
        )
    ''', re.VERBOSE)
    return ansi_escape.sub('', s)

# Import sys and define the Tee class
class Tee(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            # Check if the file is a terminal (stdout/stderr)
            if hasattr(f, 'isatty') and f.isatty():
                f.write(obj)
            else:
                # Remove ANSI codes before writing to file
                f.write(strip_ansi_codes(obj))
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

def verbose_print(args, *messages):
    if not args.quiet:
        print(*messages)

def main():
    try:
        # Clear the log file at the start of each run
        with open('RUN_LOG_FILE.log', 'w', encoding='utf-8') as log_file:
            log_file.write("")  # Pusty zapis, aby wyczyścić zawartość pliku

        # ANSI color
        COLORS = ['\033[38;5;46m',    # Green
                '\033[38;5;196m',   # Red
                '\033[38;5;214m'    # Orange
                ]
        RESET = '\033[0m'

        # Open the log file in append mode
        log_file = open('RUN_LOG_FILE.log', 'a', encoding='utf-8')

    except Exception as e:
        print(f"An error occurred: {e}")

    # Redirect sys.stdout and sys.stderr to the Tee instance
    sys.stdout = Tee(sys.__stdout__, log_file)
    sys.stderr = Tee(sys.__stderr__, log_file)

    try:

        # Define the argument parser for command-line options with RawTextHelpFormatter
        parser = argparse.ArgumentParser(
            description='''
    A script for predicting logD values based on 
    various machine learning models trained on 
    the representation of NMR spectra derived 
    from the NMRshiftDB2 database predictor. 
    
    To obtain logD values, SMILES codes of compounds 
    are sufficient. You can choose between models 
    trained on data of 1H NMR spectra, 13C NMR spectra, 
    or hybrid represntation (Best Model). The 1H spectrum option is the fastest, 
    while 13C spectra significantly lengthen the 
    prediction process. Hybrid consume combned timne of 1H 
    and 13C so it's the slowest one. Data after prediction is 
    displayed in the terminal and saved to *.CSV files.
    The input CSV file must contain at least two 
    columns of data with corresponding header names. 
    The first column “MOLECULE_NAME” contains code 
    names of compounds, and the second “SMILES” 
    structural codes of compounds. 
    
    SMILES codes can be in canonical, or Daylight 
    format. Codes from CHEMAXON that contain 
    additional | | operators will not work.

    The script can be run with options:
    1. --debug: If set, the script will not delete 
       all intermediate temporary files after execution.
       This is useful for debugging.

    2. --models: Displays the models' training data, 
       including their post-training metrics and 
       training set information.
            ''',
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        parser.add_argument(
            "csv_path",
            type=str,
            help="Path to the input CSV file containing SMILES strings."
        )
        
        parser.add_argument(
            "--predictor",
            type=str,
            default='all',
            required=False,
            choices=['1H', '13C', 'FP', 'hybrid'],  # Restricting choices to valid ones
            help="Select the type of predictive models: '1H', '13C', 'FP' or 'hybrid'."
        )
        
        parser.add_argument(
            "--debug",
            action='store_true',
            help="If set, the script will NOT delete intermediate temporary files after execution."
        )
        
        parser.add_argument(
            "--models",
            action="store_true",
            help="If set, the script will display a table with model details and metrics."
        )
        
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress most terminal output, showing only final results."
        )

        parser.add_argument(
            "--chart",
            action="store_true",
            help="Print results on designed plot."
        )
        
        parser.add_argument("--use_svr", action="store_true", help="Enable SVR predictor.")
        parser.add_argument("--use_xgb", action="store_true", help="Enable XGB predictor.")
        parser.add_argument("--use_dnn", action="store_true", help="Enable DNN predictor.")
        parser.add_argument("--use_cnn", action="store_true", help="Enable CNN predictor.")

        # Parse the command-line arguments
        args = parser.parse_args()
    
        # Clear the console and display the ASCII art logo
        subprocess.call('cls' if os.name == 'nt' else 'clear', shell=True)
        
        print_pred = args.predictor if args.predictor in ['1H', '13C'] else "1H | 13C" if args.predictor == 'hybrid' else "FingerPrints"

        print('')
        ascii_art_predictor = text2art("PREDICTOR")
        second_line = "logD"
        ascii_art_2nd_line = text2art(second_line)
        ascii_art_3rd_line = text2art(print_pred)
        art_width = len(ascii_art_predictor.split('\n')[0])
        centered_2nd_line = "\n".join(line.center(art_width) for line in ascii_art_2nd_line.split('\n'))
        centered_3rd_line = "\n".join(line.center(art_width) for line in ascii_art_3rd_line.split('\n'))
        final_art = f"{ascii_art_predictor}\n{centered_2nd_line}\n{centered_3rd_line}"
        print(final_art)                   

        # Step 1: Verify the CSV input file and correct any issues
        verified_csv_path = verify_csv(args.csv_path, args.quiet)
        
        # Determine the predictors to use
        predictors = [args.predictor] if args.predictor in ['1H', '13C', 'FP'] else 'hybrid'

        temp_data = []  # List to keep track of temporary directories
        mol_directory = None  # Initialize mol_directory
        predictor = args.predictor

        if predictor in ['1H', '13C', 'FP']:

            for predictor in predictors:

                temp_dirs = []  # Temporary directories for this predictor

                if predictor == 'FP':
                    # Step 2 - 4: Generate FingerPrint files
                    processed_dir = fp_generator(verified_csv_path, args.quiet)
                    temp_dirs.append(processed_dir)
                else:
                    if mol_directory is None:
                        # Step 2: Generate .mol files from SMILES strings
                        mol_directory = generate_mol_files(verified_csv_path, args.quiet)
                        temp_data.append(mol_directory)

                    # Step 3: Predict NMR spectra and save results as .csv files
                    csv_output_folder = run_java_batch_processor(mol_directory, predictor, args.quiet)
                    temp_dirs.append(csv_output_folder)
                
                    # Step 4: Perform bucketing to generate pseudo NMR spectra
                    processed_dir = bucket(csv_output_folder, predictor, args.quiet)
                    temp_dirs.append(processed_dir)
            
                # Step 5: Merge spectra in CSV format into one matrix file
                output_path, merged_dir = merger(processed_dir, verified_csv_path, predictor, args.quiet)
                temp_dirs.append(merged_dir)
            
                # Step 6: Create custom headers for the final dataset
                dataset, final_dir = custom_header(output_path, verified_csv_path, predictor, args.quiet)
                temp_dirs.append(final_dir)

                # Collect all temporary directories
                temp_data.extend(temp_dirs)
        
                # Step 7: Query ML models
                show_models_table = args.models
                query(dataset, predictor, show_models_table, args.quiet, args.chart, args.use_svr, args.use_xgb, args.use_dnn, args.use_cnn)

        elif predictor == 'hybrid':
            
            datasets = []  # List to keep track of datasets for hybrid prediction

            predictors = ['1H', '13C']  # Use both 1H and 13C predictors for hybrid
            for sub_predictor in predictors:
                temp_dirs = []  # Temporary directories for this predictor

                if mol_directory is None:
                    # Step 2: Generate .mol files from SMILES strings
                    mol_directory = generate_mol_files(verified_csv_path, args.quiet)
                    temp_data.append(mol_directory)

                # Step 3: Predict NMR spectra and save results as .csv files
                csv_output_folder = run_java_batch_processor(mol_directory, sub_predictor, args.quiet)
                temp_dirs.append(csv_output_folder)
            
                # Step 4: Perform bucketing to generate pseudo NMR spectra
                processed_dir = bucket(csv_output_folder, sub_predictor, args.quiet)
                temp_dirs.append(processed_dir)

                # Step 5: Merge spectra in CSV format into one matrix file
                output_path, merged_dir = merger(processed_dir, verified_csv_path, sub_predictor, args.quiet)
                temp_dirs.append(merged_dir)
            
                # Step 6: Create custom headers for the final dataset
                dataset, final_dir = custom_header(output_path, verified_csv_path, sub_predictor, args.quiet)
                temp_dirs.append(final_dir)
                datasets.append(dataset)  # Collect dataset for hybrid prediction

                # Collect all temporary directories
                temp_data.extend(temp_dirs)

            # Step 7: Generate concatenated 1H|13C input files
            dataset2, concat_dir = concatenate(datasets, args.quiet)
            temp_data.append(concat_dir)

            verbose_print(args, f'{predictor}')

            # Step 8: Query ML models
            show_models_table = args.models
            query(dataset2, predictor, show_models_table, args.quiet, args.chart, args.use_svr, args.use_xgb, args.use_dnn, args.use_cnn)

        # Optional: Clean up temporary dirs and data unless the --debug flag is set
        if not args.debug:
            verbose_print(args, 
                f"\nAll temporary files "
                f"and folders will be removed:\n"
            )

            while temp_data:  # Continue until temp_data is empty
                folder = temp_data.pop()  # Pop the last item to ensure each is processed only once

                if os.path.exists(folder):
                    shutil.rmtree(folder)
                    verbose_print(args, f"Temporary folder {COLORS[2]}'{folder}'{RESET} has been deleted.")
                else:
                    verbose_print(args, f"Folder {COLORS[1]}'{folder}'{RESET} does not exist.")

            # Delete the verified CSV file
            if os.path.exists(verified_csv_path):
                os.remove(verified_csv_path)
                verbose_print(args, f"The file {COLORS[2]}'{verified_csv_path}'{RESET} has been deleted.")
            else:
                verbose_print(args, f"The file {COLORS[1]}'{verified_csv_path}'{RESET} does not exist.")

        else:
            verbose_print(args, f"\nScript executed with the {COLORS[2]}--debug {RESET}option. All temporary files remain.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Restore original sys.stdout and sys.stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # Close the log file
        log_file.close()
    
    input(f"{COLORS[0]}\nPress ENTER to close terminal window.\n{RESET}")
    

if __name__ == "__main__":
    main()
