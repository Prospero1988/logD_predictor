# bucket.py

import os
import csv
import numpy as np


def bucket(directory, predictor):
    """
    Function to bucket NMR spectra data based on the type of predictor
    (1H or 13C).

    Parameters:
    - directory: Directory containing input CSV files with spectra data.
    - predictor: Type of NMR predictor ('1H' or '13C').

    Returns:
    - processed_dir: Directory path where bucketed spectra files are stored.
    """
    if predictor == "1H":
        sw_min, sw_max = -1, 14
    elif predictor == "13C":
        sw_min, sw_max = -10, 230

    def create_buckets():
        bucket_range = np.linspace(sw_min, sw_max, 251)
        buckets = {i: 0 for i in range(250)}
        return bucket_range, buckets

    def find_bucket_index(value, bucket_range):
        if value < sw_min or value > sw_max:
            return None
        for i in range(len(bucket_range) - 1):
            if bucket_range[i] <= value < bucket_range[i + 1]:
                return i
        return len(bucket_range) - 2

    def process_file(file_path, output_dir, bucket_range):
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            buckets = {i: 0 for i in range(250)}
            error_values = []

            for row in reader:
                try:
                    value = float(row[0])
                    bucket_index = find_bucket_index(value, bucket_range)
                    if bucket_index is not None:
                        buckets[bucket_index] += 1
                    else:
                        error_values.append(value)
                except ValueError:
                    error_values.append(row[0])

            output_file_path = os.path.join(
                output_dir, os.path.basename(file_path)
            )
            with open(output_file_path, 'w') as out_f:
                for i in range(250):
                    out_f.write(f"{buckets[i]}\n")

            return error_values

    bucket_range, _ = create_buckets()
    processed_dir = os.path.join(os.getcwd(), f'bucketed_{predictor}_spectra')
    os.makedirs(processed_dir, exist_ok=True)

    success_count = 0
    error_files = {}

    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            error_values = process_file(file_path, processed_dir, bucket_range)

            if error_values:
                error_files[filename] = error_values
            else:
                success_count += 1

    print(f"\nSuccessfully created {success_count} files as pseudo spectra.")
    if error_files:
        print(f"Files with errors: {len(error_files)}")
        for fname, errors in error_files.items():
            print(f"{fname}: {errors}")

    return processed_dir
