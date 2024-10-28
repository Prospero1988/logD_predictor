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

# Import custom modules required for the script
from logD_predictor_bin.csv_checker import verify_csv
from logD_predictor_bin.gen_mols import generate_mol_files
from logD_predictor_bin.predictor import run_java_batch_processor
from logD_predictor_bin.bucket import bucket
from logD_predictor_bin.merger import merger
from logD_predictor_bin.custom_header import custom_header
from logD_predictor_bin.model_query_temp import query
from logD_predictor_bin.fp_generator import fp_generator

# Import sys and define the Tee class
import sys

class Tee(object):
    def __init__(self, *files):
        self.files = files
    
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()

def verbose_print(args, *messages):
    if not args.quiet:
        print(*messages)

def main():
    
    # ANSI color
    COLORS = ['\033[38;5;46m',    # Green
              '\033[38;5;196m',   # Red
              '\033[38;5;214m'    # Orange
             ]
    RESET = '\033[0m'

    # Open the log file in append mode
    log_file = open('predictor_logD.log', 'a', encoding='utf-8')

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
    or both. The 1H spectrum option is the fastest, 
    while 13C spectra significantly lengthen the 
    prediction process. Data after prediction is 
    displayed in the terminal and saved to *.CSV files.
    The input CSV file must contain at least two 
    columns of data with corresponding header names. 
    The first column “MOLECULE_NAME” contains code 
    names of compounds, and the second “SMILES” 
    structural codes of compounds. 
    
    SMILES codes can be in canonical, or Daylight 
    format. Codes from CHEMAXON that contain 
    additional | | operators will not work.

    The script can be run with two options:
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
            choices=['1H', '13C', 'FP', 'all'],  # Restricting choices to valid ones
            help="Select the type of predictive models: '1H', '13C', 'FP' or 'all'."
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

        # Parse the command-line arguments
        args = parser.parse_args()
    
        # Clear the console and display the ASCII art logo
        subprocess.call('cls' if os.name == 'nt' else 'clear', shell=True)
        
        print('')
        ascii_art_predictor = text2art("PREDICTOR")
        second_line = "logD"
        ascii_art_2nd_line = text2art(second_line)
        art_width = len(ascii_art_predictor.split('\n')[0])
        centered_2nd_line_lines = [line.center(art_width) for line in ascii_art_2nd_line.split('\n')]
        final_art = f"{ascii_art_predictor}\n" + "\n".join(centered_2nd_line_lines)
        print(final_art)                   

        # Step 1: Verify the CSV input file and correct any issues
        verified_csv_path = verify_csv(args.csv_path, args.quiet)
        
        # Determine the predictors to use
        predictors = [args.predictor] if args.predictor in ['1H', '13C', 'FP'] else ['1H', '13C', 'FP']

        temp_data = []  # List to keep track of temporary directories
        mol_directory = None  # Initialize mol_directory

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
            query(dataset, predictor, show_models_table, args.quiet)
            
        # Optional: Clean up temporary dirs and data unless the --debug flag is set
        if not args.debug:
            verbose_print(args, 
                f"\nAll temporary files "
                f"and folders will be removed:\n"
            )
            # Use set to avoid duplicates in temp_data
            for folder in set(temp_data):
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

            # Delete mol_directory if it was created
            if mol_directory and os.path.exists(mol_directory):
                shutil.rmtree(mol_directory)
                verbose_print(args, f"Temporary folder {COLORS[2]}'{mol_directory}'{RESET} has been deleted.")
            elif mol_directory:
                verbose_print(args, f"Folder {COLORS[1]}'{mol_directory}'{RESET} does not exist.")
        else:
            verbose_print(args, f"\nScript executed with the {COLORS[2]}--debug {RESET}option. All temporary files remain.")
        
    finally:
        # Restore original sys.stdout and sys.stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # Close the log file
        log_file.close()
    
    print(f"{COLORS[0]}\nEND OF THE SCRIPT\n{RESET}")

if __name__ == "__main__":
    main()
