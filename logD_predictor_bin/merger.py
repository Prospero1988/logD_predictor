# merger.py

import pandas as pd
import os


def merger(processed_dir, csv_path):
    """
    Merges multiple CSV files in the specified directory into a single
    DataFrame,
    adds filename information, and saves the result as a new CSV file.

    Parameters:
    - processed_dir (str): Directory containing the individual CSV files to be
                           merged.
    - csv_path (str): Path to an initial CSV file used to generate the name of
                      the merged output file.

    Returns:
    - output_path (str): Path to the merged CSV file.
    - merged_dir (str): Path to the directory where the merged CSV file
    is saved.
    """
    try:
        merging_directory = os.path.join(os.getcwd(), processed_dir)
        if not os.path.exists(merging_directory):
            print(f"{merging_directory} does not exist.")
            return

        csv_files = [file for file in os.listdir(merging_directory)
                     if file.endswith(".csv")]
        csv_files.sort()

        df_merged = pd.DataFrame()
        for file in csv_files:
            file_path = os.path.join(merging_directory, file)
            df_temp = pd.read_csv(file_path, header=None)
            df_temp = df_temp.transpose()
            filename_without_extension = os.path.splitext(file)[0]
            df_temp.insert(0, 'filename', filename_without_extension)
            df_merged = pd.concat([df_merged, df_temp], ignore_index=True)

        merged_dir = os.path.join(os.getcwd(), 'merged')
        if not os.path.exists(merged_dir):
            print(f"\n{merged_dir} directory has been created.")
            os.makedirs(merged_dir, exist_ok=True)

        file_name = os.path.basename(csv_path).split('.')[0] + '_merged.csv'
        output_path = os.path.join(merged_dir, file_name)

        df_merged.to_csv(output_path, index=False, header=True)
        print(f"\nMerged file saved as: {os.path.basename(output_path)} in "
              f"{merged_dir}")

    except Exception as e:
        print(f"An error occurred: {e}")

    return output_path, merged_dir
