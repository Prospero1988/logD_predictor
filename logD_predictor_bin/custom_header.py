# custom_header.py

import os
import pandas as pd

def custom_header(output_path, csv_path, predictor, quiet=False):
    """
    Adds custom headers to the provided DataFrame based on the number of
    columns and saves it as a new CSV file.

    Parameters:
    - labeled (pd.DataFrame): The DataFrame to which custom headers will
      be added.
    - csv_path (str): The path to the CSV file used to generate the new
      filename.
    - predictor (str): Type of NMR predictor.

    Returns:
    - None
    """
    
    # Defining the function that controls printing
    def verbose_print(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    # ANSI color
    COLORS = ['\033[38;5;46m',    # Green
              '\033[38;5;196m',   # Red
              '\033[38;5;214m'    # Orange
             ]
    RESET = '\033[0m'
    
    try:
        
        merged = pd.read_csv(output_path)
        header_list = ["MOLECULE_NAME"]
        number_of_columns = len(merged.columns) - 1

        for counter in range(1, number_of_columns + 1):
            header_list.append(f"FEATURE_{counter}")

        if len(header_list) == len(merged.columns):
            merged.columns = header_list
            dataset = merged.copy()
        else:
            print(f"{COLORS[1]}Error: Headers count ({len(header_list)}) does not match {RESET}"
                  f"{COLORS[1]}columns count ({len(merged.columns)}).{RESET}")
            
        final_dir = os.path.join(os.getcwd(), f'{predictor}_generated_ML_querries')
        os.makedirs(final_dir, exist_ok=True)

        file_name = os.path.basename(csv_path).rsplit('.', 1)[0].rsplit('_', 1)[0]
        file_name = os.path.join(final_dir, f"{file_name}_{predictor}_ML_querry.csv")

        merged.to_csv(file_name, index=False)
        verbose_print(f"\nFinal ML querry file saved as: {COLORS[2]}{os.path.basename(file_name)}{RESET}"
              f" in {COLORS[2]}{final_dir}{RESET}\n")

    except Exception as e:
        print(f"{COLORS[1]}Error occurred: {e}{RESET}")
        dataset = None
        
    return dataset, final_dir
