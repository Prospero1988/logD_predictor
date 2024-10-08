# csv_checker.py

import pandas as pd
import csv


def verify_csv(file_path):
    """
    Function to verify and modify a CSV file by handling separators, decimal
    points, and column structure. Additionally, it cleans up the first column
    (e.g., molecule names) by removing problematic characters.

    Parameters:
    - file_path: The path to the input CSV file to be verified.

    Returns:
    - verified_file_path: Path to the newly saved CSV file with '_verified'
                          suffix,
                          or None if there was an error in processing the file.
    """
    try:
        print(f"\nStarting verification of the file: {file_path}")
        print("\nDetecting column separator...")
        with open(file_path, 'r') as file:
            sample = file.read(2048)

        delimiter_candidates = [',', ';', '\t']
        delimiter_counts = {delim: sample.count(delim) for delim in
                            delimiter_candidates}
        separator = max(delimiter_counts, key=delimiter_counts.get)
        print(f"\nDetected column separator: '{separator}'")

        print("\nReading header to determine expected number of columns...")
        with open(file_path, 'r') as file:
            reader = csv.reader(file, delimiter=separator)
            headers = next(reader)
            expected_columns = len(headers)
            print(f"\nExpected number of columns: {expected_columns}")

        print("\nLoading CSV file with detected separator, "
              "skipping malformed rows...")
        df = pd.read_csv(file_path, delimiter=separator, on_bad_lines='skip')
        print(f"\nLoaded CSV file with shape: {df.shape}")

    except Exception as e:
        print(f"\nError reading file or detecting delimiter: {e}")
        return None

    try:
        if separator == ';':
            print("\nSeparator is semicolon. Checking for decimal commas...")

            def is_comma_decimal(cell):
                try:
                    cell_str = str(cell)
                    return ',' in cell_str and '.' not in cell_str and float(
                        cell_str.replace(',', '.')
                    )
                except ValueError:
                    return False

            if df.applymap(is_comma_decimal).any().any():
                print("\nDetected commas as decimal points. Replacing "
                      "with dots...")
                df = df.applymap(
                    lambda x: x.replace(',', '.') if isinstance(x, str) and
                    is_comma_decimal(x) else x
                )
                print("\nReplaced decimal commas with dots.")
            else:
                print("\nNo decimal commas detected.")

        column_count = len(df.columns)
        print(f"\nNumber of columns in the CSV file: {column_count}")
        if column_count > 3:
            print("\nRemoving excess columns...")
            df = df.iloc[:, :3]
            print(f"\nReduced to {df.shape[1]} columns.")

        verified_file_path = file_path.replace('.csv', '_verified.csv')
        if separator == ';':
            df.to_csv(verified_file_path, index=False, sep=',')
        else:
            df.to_csv(verified_file_path, index=False, sep=separator)

        print("\nCleaning up the first column (molecule names)...")

        def clean_molecule_name(name):
            if isinstance(name, str):
                name = name.strip().replace(" ", "").replace("\t", "")
                for char in ['*', '&', '^', '%', '$', '@', '!', '~', '#', '(',
                             ')', '[', ']', '{', '}', '?', '/', '\\']:
                    name = name.replace(char, "_")
                return name
            return name

        df.iloc[:, 0] = df.iloc[:, 0].apply(clean_molecule_name)
        df.to_csv(verified_file_path, index=False, sep=',')
        print(f"\nCSV file saved at: {verified_file_path}")

    except Exception as e:
        print(f"\nError processing CSV file: {e}")
        return None

    print("\nVerification and modifications completed successfully.")
    return verified_file_path
