# custom_header.py

import os


def custom_header(labeled, csv_path, predictor):
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
    try:
        header_list = ["MOLECULE_NAME", "LABEL"]
        number_of_columns = len(labeled.columns) - 2

        for counter in range(1, number_of_columns + 1):
            header_list.append(f"FEATURE_{counter}")

        if len(header_list) == len(labeled.columns):
            labeled.columns = header_list
        else:
            print(f"Error: Headers count ({len(header_list)}) does not match "
                  f"columns count ({len(labeled.columns)}).")

        final_dir = os.path.join(os.getcwd(), 'generated_ML_inputs')
        os.makedirs(final_dir, exist_ok=True)

        file_name = os.path.basename(csv_path).rsplit('.', 1)[0].rsplit('_', 1)[0]
        file_name = os.path.join(final_dir, f"{file_name}_{predictor}_ML_input.csv")

        labeled.to_csv(file_name, index=False)
        print(f"\nFinal ML INPUT file saved as: {os.path.basename(file_name)} "
              f"in {final_dir}\n")

    except Exception as e:
        print(f"Error occurred: {e}")
