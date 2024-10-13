
# README for logD_predictor Project
## logD Predictor

logD_predictor is a versatile command-line tool designed to predict the distribution coefficient (logD) of chemical compounds based on theoretical NMR spectra. This pipeline facilitates the complete workflow, starting from processing SMILES strings to predicting NMR spectra, bucketing, and generating machine learning model predictions for logD at different pH levels.

The tool uses the NMRshiftDB2 predictor, which can be accessed here.

## Table of Contents

- Features
- Installation
- Usage
- Input File Format
- Output File Description
- Project Structure
- Dependencies
- Troubleshooting
- License

## Features

- **CSV File Verification**: Automatically detects separators, checks for decimal inconsistencies, and cleans molecule names to ensure consistent input files.
- **Molecule File Generation**: Converts SMILES strings from the CSV input to .mol files, suitable for further processing.
- **NMR Spectra Prediction**: Uses a Java-based batch processor from the NMRshiftDB2 predictor to generate theoretical NMR spectra for 1H and 13C nuclei.
- **Spectra Bucketing**: Converts continuous spectra data into discrete buckets for machine learning model compatibility.
- **Model Querying**: Queries pre-trained machine learning models to predict logD values based on the bucketed NMR spectra.
- **Automated Cleanup**: Option to remove all temporary files generated during the execution.

## Installation

- Clone the repository:

  ```
  git clone https://github.com/yourusername/logD_predictor.git
  cd logD_predictor
  ```

- Install required Python packages:

  ```
  python install_modules.py
  ```

- Set up Java environment:
  - Install the Java SDK, ensuring that `javac` and `java` commands are accessible in your system's PATH.
  - The script uses Java batch processors located in the predictor directory. Ensure that the `.jar` and `.java` files are correctly configured.
  - **Important**: The script was tested under Windows 10 using PowerShell and works reliably in this environment on Python 3.11.4. It has not been tested on Linux or other operating systems.

## Usage

To run the logD predictor, use the following command:

```
python logD_predictor.py --csv_path path/to/your/input.csv [--clean]
```

### Arguments

- `--csv_path`: (Required) Path to the input CSV file containing SMILES strings for the molecules.
- `--clean`: (Optional) If set, the script deletes all intermediate files and directories after completion.

## Input File Format

The input file should be a CSV file containing at least the following columns:

- **MOLECULE_NAME**: Name or identifier of the molecule.
- **SMILES**: SMILES representation of the molecule structure.

Example:

```
MOLECULE_NAME,SMILES
Molecule_1,CCO
Molecule_2,CCN(CC)CC
```

A sample input file `input_example.csv` is provided in the repository for reference.

## Output File Description

- **Verified CSV**: The initial input CSV is processed and saved as `<original_filename>_verified.csv`.
- **MOL Files**: Each molecule's SMILES string is converted into a `.mol` file located in the `mols` directory.
- **NMR Spectra CSVs**: Generated theoretical spectra are saved in the `predicted_spectra_1H` and `predicted_spectra_13C` directories.
- **Bucketed Spectra CSVs**: Bucketed spectra files are stored in the `bucketed_1H_spectra` and `bucketed_13C_spectra` directories.
- **Merged CSV**: The spectra CSVs are merged into a single file named `<original_filename>_merged.csv`.
- **ML Model Predictions**: Predicted logD values are saved as `<original_filename>_<predictor>_query_results.csv`.

## Project Structure

```
logD_predictor/
│
├── logD_predictor.py              # Main script for executing the pipeline
├── install_modules.py             # Installs required Python packages
├── predictor/
│   ├── predictorh.jar             # Java-based predictor for 1H spectra
│   ├── predictor13C.jar           # Java-based predictor for 13C spectra
│   ├── cdk-2.9.jar                # CDK library required for spectrum prediction.
│   ├── BatchProcessor1H.java      # Java batch processor for 1H spectra
│   └── BatchProcessor13C.java     # Java batch processor for 13C spectra
├── logD_predictor_bin/            # Directory containing helper modules
│   ├── csv_checker.py             # Verifies and preprocesses CSV files
│   ├── gen_mols.py                # Generates .mol files from SMILES strings
│   ├── bucket.py                  # Buckets NMR spectra
│   ├── merger.py                  # Merges bucketed spectra CSVs
│   ├── custom_header.py           # Adds custom headers to the final dataset
│   ├── models.py                  # Paths and names of ML models
│   └── model_query.py             # Queries machine learning models
├── input_example.csv              # Sample input CSV file with SMILES strings
└── README.md                      # Project documentation (this file)
```

## Dependencies

The following dependencies are required and can be installed using the `install_modules.py` script:

- `numpy`
- `pandas`
- `rdkit`
- `tqdm`
- `art`

Additionally, Java is required to compile and run the batch processors for NMR spectra prediction.

## Troubleshooting

- **Java Compilation Issues**: Ensure that Java is installed and that the `javac` and `java` commands are accessible.
- **Python Module Errors**: If any Python modules are missing, ensure that all dependencies are installed as per the `install_modules.py` script.
- **File Path Issues**: Ensure that all paths are correctly specified, particularly when working with large directories or nested files.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Additional Features

- **Dynamic Progress Bars**:
  - The script contains two dynamic progress bars:
    1. **Molecular File Generation**: Tracks the process of converting SMILES to `.mol` files, showing progress in real-time in the terminal.
    2. **NMR Prediction**: Displays the progress during the machine learning prediction step for CHI logD values based on the generated `.mol` files.

- **Colorized Terminal Output**:
  - The terminal output is enhanced with ANSI colors to highlight important messages such as progress updates, errors, and success notifications.

## Argument `--models`

- If you include the `--models` argument when running the script, the tool will display detailed metrics for the machine learning models used during prediction. These metrics include model names, algorithms, datasets used, and post-training performance metrics such as RMSE, MAE, R2, and PEARSON correlation.

## `joblib_models` Directory

- The `joblib_models` directory contains CSV files that define the models used for predicting CHI logD values. Each CSV file corresponds to a different type of NMR spectrum (e.g., `1H_models_info.csv`, `13C_models_info.csv`). These files include information such as:
  - **Model Name**: The name of the machine learning model.
  - **Model Path**: The path to the pre-trained model saved in `.joblib` format.
  - **Performance Metrics**: Metrics like RMSE, MAE, R2, and PEARSON that summarize the model's performance.

Make sure that the correct model definition files are present in this folder before running predictions. The script will load the models dynamically from these CSV files and apply them to the processed NMR spectra.

## Example Usage

Run the following command for the complete workflow:

```bash
python logD_predictor.py --csv_path my_input.csv --predictor 1H --models --clean
```

- Replace `my_input.csv` with the path to your input file containing SMILES codes.
- The `--models` flag shows details of the models used during prediction.
- The `--clean` flag removes all intermediate files after execution. Omit this flag if you wish to keep the intermediate files for debugging.

## Output File Structure

- **logD_results/**: Directory containing the final output files with predicted logD values.
  - Example output file: `my_input_1H_query_results.csv`.
