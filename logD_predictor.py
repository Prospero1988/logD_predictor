#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script Name: logD_predictor.py
Description: 
"""

import argparse
import shutil
import os
import subprocess
from art import text2art

# Import custom modules required for the script
#from demiurge_bin.csv_checker import verify_csv
#from demiurge_bin.gen_mols import generate_mol_files
#from demiurge_bin.predictor import run_java_batch_processor
#from demiurge_bin.bucket import bucket
#from demiurge_bin.merger import merger
#from demiurge_bin.labeler import labeler
#from demiurge_bin.custom_header import custom_header

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
        ascii_art_demiurge = text2art("DEMIURGE")
        predictor = args.predictor
        ascii_art_predictor = text2art(predictor)
        art_width = len(ascii_art_demiurge.split('\n')[0])
        centered_predictor_lines = [line.center(art_width) for line in ascii_art_predictor.split('\n')]
        final_art = f"{ascii_art_demiurge}\n" + "\n".join(centered_predictor_lines)
        print(final_art)                   

        # Step 1: Verify the CSV input file and correct any issues
        verified_csv_path = verify_csv(args.csv_path)
    
        # Step 2: Generate .mol files from SMILES strings
        mol_directory = generate_mol_files(verified_csv_path)
    
        # Step 3: Predict NMR spectra and save results as .csv files
        csv_output_folder = run_java_batch_processor(mol_directory, args.predictor)
    
        # Step 4: Perform bucketing to generate pseudo NMR spectra
        processed_dir = bucket(csv_output_folder, args.predictor)
    
        # Step 5: Merge spectra in CSV format into one matrix file
        output_path, merged_dir = merger(processed_dir, verified_csv_path)
    
        # Step 6: Insert labels into the merged files
        labeled = labeler(
            verified_csv_path, output_path, args.label_column, merged_dir
        )
    
        # Step 7: Create custom headers for the final dataset
        custom_header(labeled, verified_csv_path, args.predictor)
    
        # Optional: Clean up temporary dirs and data if the --clean flag is set
        if args.clean:
            print(
                "Script executed with the --clean option. All temporary files "
                "and folders will be removed:\n"
            )
            temp_data = [
                mol_directory, csv_output_folder, processed_dir, merged_dir
            ]
            for folder in temp_data:
                if os.path.exists(folder):
                    shutil.rmtree(folder)
                    print(f"Temporary folder '{folder}' has been deleted.")
                else:
                    print(f"Folder '{folder}' does not exist.")
    
    finally:
        # Restore original sys.stdout and sys.stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # Close the log file
        log_file.close()
    
    print("\nEND OF THE SCRIPT\n")

if __name__ == "__main__":
    main()
