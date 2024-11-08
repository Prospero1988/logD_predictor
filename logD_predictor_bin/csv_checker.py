import pandas as pd
import csv
import os

def verify_csv(file_path, quiet=False):
    """
    Function to verify and modify a CSV file by handling separators, decimal
    points, and column structure. Additionally, it cleans up the first column
    (e.g., molecule names) by removing problematic characters.
    
    If any rows are malformed (i.e., column count mismatch), they are reported.
    """
    # Definiowanie funkcji kontrolującej drukowanie
    def verbose_print(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    # ANSI color
    COLORS = ['\033[38;5;46m',    # Green
              '\033[38;5;196m',   # Red
              '\033[38;5;214m'    # Orange
             ]
    RESET = '\033[0m'

    # Check if input file exists
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                verbose_print(f"\nRead file {COLORS[2]}{file_path}{RESET}")
        except Exception as e:
            print(f"{COLORS[1]}Error reading the file {file_path}.\n{e}\n{RESET}")
            exit(1)
    else:
        print(f"{COLORS[1]}File {file_path} does not exist.{RESET}")
        exit(1)

    try:
        verbose_print(f"\nStarting verification of the file.")
        verbose_print("\nDetecting column separator...")
        with open(file_path, 'r') as file:
            sample = file.read(2048)

        delimiter_candidates = [',', ';', '\t']
        delimiter_counts = {delim: sample.count(delim) for delim in delimiter_candidates}
        separator = max(delimiter_counts, key=delimiter_counts.get)
        verbose_print(f"\nDetected column separator: {COLORS[2]}'{separator}'{RESET}")

        verbose_print("\nReading header to determine expected number of columns...")
        with open(file_path, 'r') as file:
            reader = csv.reader(file, delimiter=separator)
            headers = next(reader)
            expected_columns = len(headers)
            verbose_print(f"\nExpected number of columns: {COLORS[2]}{expected_columns}{RESET}")

        verbose_print("\nLoading CSV file and checking for malformed rows...")
        
        # Track malformed rows
        malformed_rows = []

        # Read the file line by line and check for column mismatch
        with open(file_path, 'r') as file:
            reader = csv.reader(file, delimiter=separator)
            for i, row in enumerate(reader):
                if len(row) != expected_columns:
                    malformed_rows.append(i + 1)  # Track row numbers (starting from 1)
                    print(f"\n{COLORS[1]}Warning: Malformed row {i + 1} (expected {expected_columns} columns, found {len(row)} columns): \n{row}{RESET}")
        
        if malformed_rows:
            print(f"\n{COLORS[1]}Total malformed rows: {len(malformed_rows)}{RESET}\n"
                  f"{COLORS[1]}Malformed rows will not be used in further processing.{RESET}")
        else:
            verbose_print(f"\n{COLORS[0]}No malformed rows detected.{RESET}")

        # Load the data, skipping malformed rows
        df = pd.read_csv(file_path, delimiter=separator, on_bad_lines='skip')
        verbose_print(f"\nLoaded CSV file with shape: {COLORS[2]}{df.shape}{RESET}")

    except Exception as e:
        print(f"\n{COLORS[1]}Error reading file or detecting delimiter: {e}{RESET}")
        return None

    try:
        if separator == ';':
            verbose_print(f"\nSeparator is {COLORS[2]}semicolon{RESET}. Checking for decimal commas...")

            def is_comma_decimal(cell):
                try:
                    cell_str = str(cell)
                    return ',' in cell_str and '.' not in cell_str and float(
                        cell_str.replace(',', '.')
                    )
                except ValueError:
                    return False

            if df.map(is_comma_decimal).any().any():
                verbose_print("\nDetected commas as decimal points. Replacing with dots...")
                df = df.map(
                    lambda x: x.replace(',', '.') if isinstance(x, str) and is_comma_decimal(x) else x
                )
                verbose_print(f"\n{COLORS[0]}Replaced decimal commas with dots.{RESET}")
            else:
                verbose_print("\nNo decimal commas detected.")

        column_count = len(df.columns)
        verbose_print(f"\nNumber of columns in the CSV file: {COLORS[2]}{column_count}{RESET}")
        if column_count > 3:
            verbose_print("\nRemoving excess columns...")
            df = df.iloc[:, :3]
            verbose_print(f"\nReduced to {df.shape[1]} columns.")

        verified_file_path = file_path.replace('.csv', '_verified.csv')
        if separator == ';':
            df.to_csv(verified_file_path, index=False, sep=',')
        else:
            df.to_csv(verified_file_path, index=False, sep=separator)

        verbose_print("\nCleaning up the first column (molecule names)...")

        def clean_molecule_name(name):
            if isinstance(name, str):
                name = name.strip().replace(" ", "").replace("\t", "")
                for char in ['*', '&', '^', '%', '$', '@', '!', '~', '#', '(', ')', '[', ']', '{', '}', '?', '/', '\\']:
                    name = name.replace(char, "_")
                return name
            return name

        df.iloc[:, 0] = df.iloc[:, 0].apply(clean_molecule_name)
        df.to_csv(verified_file_path, index=False, sep=',')
        verbose_print(f"\nCSV file saved at: {COLORS[2]}{verified_file_path}{RESET}")

        # Checking for NaN values in any column and removing rows with NaN
        try:
            nan_count = df.isna().sum().sum()  # Total NaN values
            if nan_count > 0:
                df = df.dropna()  # Drop rows with any NaN value
                verbose_print(f"\n{COLORS[1]}Found {nan_count} NaN values. Rows containing NaN have been removed.{RESET}")
                df.to_csv(verified_file_path, index=False, sep=',')
            else:
                verbose_print(f"\n{COLORS[0]}No NaN values found in the file.{RESET}")
        except Exception as e:
            print(f"\n{COLORS[1]}Error while checking for NaN values: {e}{RESET}")
        
    except Exception as e:
        print(f"\n{COLORS[1]}Error processing CSV file: {e}{RESET}")
        return None

    verbose_print(f"{COLORS[0]}\nVerification and modifications completed successfully.{RESET}")
    return verified_file_path
