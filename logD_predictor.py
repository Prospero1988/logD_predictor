#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script Name: logD_predictor.py
Description: yet to be filled
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

def main():

    # Open the log file in append mode
    log_file = open('predictor_logD.log', 'a', encoding='utf-8')

    # Redirect sys.stdout and sys.stderr to the Tee instance
    sys.stdout = Tee(sys.__stdout__, log_file)
    sys.stderr = Tee(sys.__stderr__, log_file)

    try:

        # Define the argument parser for command-line options
        parser = argparse.ArgumentParser(
            description="---yet to be filled--"
        )
        parser.add_argument(
            "--csv_path",
            type=str,
            required=True,
            help="Path to the input CSV file containing SMILES strings."
        )
        parser.add_argument(
            "--clean",
            action='store_true',
            help="If set, the script deletes all intermediate temporary "
                 "files after execution."
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
        verified_csv_path = verify_csv(args.csv_path)
    
        # Step 2: Generate .mol files from SMILES strings
        mol_directory = generate_mol_files(verified_csv_path)
    
        predictors = ['1H', '13C']
    
        for predictor in predictors:
            
            # Step 3: Predict NMR spectra and save results as .csv files
            csv_output_folder = run_java_batch_processor(mol_directory, predictor)
        
            # Step 4: Perform bucketing to generate pseudo NMR spectra
            processed_dir = bucket(csv_output_folder, predictor)
        
            # Step 5: Merge spectra in CSV format into one matrix file
            output_path, merged_dir = merger(processed_dir, verified_csv_path, predictor)
        
            # Step 6: Create custom headers for the final dataset
            custom_header(output_path, verified_csv_path, predictor)
    
            # Optional: Clean up temporary dirs and data if the --clean flag is set
            if args.clean:
                print(
                    "Script executed with the --clean option. All temporary files "
                    "and folders will be removed:\n"
                )
                temp_data = [
                    csv_output_folder, processed_dir, merged_dir]
                
                for folder in temp_data:
                    if os.path.exists(folder):
                        shutil.rmtree(folder)
                        print(f"Temporary folder '{folder}' has been deleted.")
                    else:
                        print(f"Folder '{folder}' does not exist.")
        if args.clean:
            if os.path.exists(verified_csv_path):
                os.remove(verified_csv_path)
                print(f"The file '{verified_csv_path}' has been deleted.")
            else:
                print(f"The file '{verified_csv_path}' does not exist.")
            
            if os.path.exists(mol_directory):
                shutil.rmtree(mol_directory)
                print(f"Temporary folder '{mol_directory}' has been deleted.")
            else:
                print(f"Folder '{mol_directory}' does not exist.")

    finally:
        # Restore original sys.stdout and sys.stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # Close the log file
        log_file.close()
    
    print("\nEND OF THE SCRIPT\n")

if __name__ == "__main__":
    main()
