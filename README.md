### README for `logD_predictor` Project

# logD Predictor

`logD_predictor` is a versatile command-line tool designed to predict the distribution coefficient (logD) of chemical compounds based on theoretical NMR spectra. This pipeline facilitates the complete workflow, starting from processing SMILES strings to predicting NMR spectra, bucketing, and generating machine learning model predictions for logD at different pH levels.

The tool uses the NMRshiftDB2 predictor, which can be accessed [here](https://sourceforge.net/p/nmrshiftdb2/wiki/PredictorJars/).

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Input File Format](#input-file-format)
5. [Output File Description](#output-file-description)
6. [Project Structure](#project-structure)
7. [Dependencies](#dependencies)
8. [Troubleshooting](#troubleshooting)
9. [License](#license)

## Features
- **CSV File Verification**: Automatically detects separators, checks for decimal inconsistencies, and cleans molecule names to ensure consistent input files.
- **Molecule File Generation**: Converts SMILES strings from the CSV input to `.mol` files, suitable for further processing.
- **NMR Spectra Prediction**: Uses a Java-based batch processor from the [NMRshiftDB2 predictor](https://sourceforge.net/p/nmrshiftdb2/wiki/PredictorJars/) to generate theoretical NMR spectra for `1H` and `13C` nuclei.
- **Spectra Bucketing**: Converts continuous spectra data into discrete buckets for machine learning model compatibility.
- **Model Querying**: Queries pre-trained machine learning models to predict logD values based on the bucketed NMR spectra.
- **Automated Cleanup**: Option to remove all temporary files generated during the execution.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/logD_predictor.git
    cd logD_predictor
    ```

2. Install required Python packages:
    ```bash
    python install_modules.py
    ```

3. Set up Java environment:
    - Install the Java SDK, ensuring that `javac` and `java` commands are accessible in your system's PATH.
    - The script uses Java batch processors located in the `predictor` directory. Ensure that the `.jar` and `.java` files are correctly configured.
    - **Important**: The script was tested under **Windows 10** using **PowerShell** and works reliably in this environment. It has **not** been tested on Linux or other operating systems.

## Usage
To run the logD predictor, use the following command:
```bash
python logD_predictor.py --csv_path path/to/your/input.csv [--clean]
```

### Arguments
- `--csv_path`: (Required) Path to the input CSV file containing SMILES strings for the molecules.
- `--clean`: (Optional) If set, the script deletes all intermediate files and directories after completion.

## Input File Format
The input file should be a CSV file containing at least the following columns:
- `MOLECULE_NAME`: Name or identifier of the molecule.
- `SMILES`: SMILES representation of the molecule structure.

Example:
```
MOLECULE_NAME,SMILES
Molecule_1,CCO
Molecule_2,CCN(CC)CC
```

A sample input file `input_example.csv` is provided in the repository for reference.

## Output File Description
1. **Verified CSV**: The initial input CSV is processed and saved as `<original_filename>_verified.csv`.
2. **MOL Files**: Each molecule's SMILES string is converted into a `.mol` file located in the `mols` directory.
3. **NMR Spectra CSVs**: Generated theoretical spectra are saved in the `predicted_spectra_1H` and `predicted_spectra_13C` directories.
4. **Bucketed Spectra CSVs**: Bucketed spectra files are stored in the `bucketed_1H_spectra` and `bucketed_13C_spectra` directories.
5. **Merged CSV**: The spectra CSVs are merged into a single file named `<original_filename>_merged.csv`.
6. **ML Model Predictions**: Predicted logD values are saved as `<original_filename>_<predictor>_query_results.csv`.

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
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
