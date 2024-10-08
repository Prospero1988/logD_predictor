# labeler.py

import pandas as pd
import os


def labeler(csv_path, output_path, label_column, merged_dir):
    """
    Adds labels from a source CSV file to a merged NMR DataFrame based on a
    specified column and saves the result as a new CSV file.

    Parameters:
    - csv_path (str): Path to the CSV file containing labels and
      'MOLECULE_NAME'.
    - output_path (str): Path to the merged CSV file containing NMR data.
    - label_column (int): Column index (1-based) in the label CSV file that
                          contains labels to be added.
    - merged_dir (str): Directory where the labeled CSV file will be saved.

    Returns:
    - labeled (pd.DataFrame): The labeled DataFrame after adding the specified
                              labels.
    """
    try:
        labels_csv = pd.read_csv(csv_path)
        merged_nmr = pd.read_csv(output_path)

        label_column = label_column - 1
        label_column_name = labels_csv.columns[label_column]

        labeled = pd.merge(merged_nmr,
                           labels_csv[['MOLECULE_NAME', label_column_name]],
                           left_on='filename', right_on='MOLECULE_NAME',
                           how='left')

        labeled['LABEL'] = labeled[label_column_name]
        labeled.drop(columns=['MOLECULE_NAME', label_column_name],
                     inplace=True)

        cols = list(labeled.columns)
        cols.insert(1, cols.pop(cols.index('LABEL')))
        labeled = labeled[cols]

        file_name = os.path.join(merged_dir,
                                 os.path.basename(csv_path).split('.')[0] +
                                 '_labeled.csv')

        labeled.to_csv(file_name, index=False)
        print(f'\nColumn {label_column_name} successfully copied'
              f' from {os.path.basename(csv_path)}'
              f" to {os.path.basename(output_path)}.")

    except Exception as e:
        print(f"Error occurred: {e}")

    return labeled
