
# LogD Predictor - NMR Spectra Machine Learning Model Predictions

This project provides a machine learning-based solution for predicting CHI logD values from NMR spectra, specifically using 1H and 13C NMR models. The tool uses CSV files containing SMILES codes as inputs, and outputs CSV files with predicted logD values based on trained models.

## Setup and Installation

1. **Dependencies**:
   Make sure to install the following dependencies using the provided `requirements.txt` or manually:

   ```
   pip install -r requirements.txt
   ```
   Or manually install:
   - `pandas`
   - `rdkit`
   - `joblib`

2. **Folder Structure**:
   After cloning the repository, the folder structure is as follows:

   ```
   project-root/
   ├── logD_predictor.py
   ├── model_query.py
   ├── gen_mols.py
   ├── logD_predictor_bin/
   │   ├── csv_checker.py
   │   ├── predictor.py
   │   ├── gen_mols.py
   │   └── joblib_models/    # CSV files with model definitions (semicolon-separated)
   ├── mols/                 # Folder for generated .mol files
   └── logD_results/         # Folder for prediction results
   ```

## Usage

The main script `logD_predictor.py` handles the entire pipeline from SMILES to CHI logD predictions. It accepts the following command-line arguments:

- `--csv_path` (required): Path to the input CSV file containing SMILES codes.
- `--predictor` (required): Model to use for predictions (`1H`, `13C`, or `both`).
- `--models` (optional): Displays detailed model metrics and information.
- `--clean` (optional): Cleans up all temporary files after script execution.

### Example Usage:

```bash
python logD_predictor.py --csv_path myfile.csv --predictor 1H --clean
```

## Features

### 1. Generate `.mol` Files from SMILES

The `gen_mols.py` script converts SMILES codes to `.mol` format. Progress is displayed with a dynamic progress bar in the terminal, using colored output to track the process of generating these molecular files.

### 2. Model Predictions on NMR Spectra

Predictions are made using trained machine learning models. The `model_query.py` script reads the model definition CSVs from the `joblib_models` folder and performs the predictions. Results are saved as a CSV file, with a colored dynamic progress bar showing the prediction progress.

### 3. Colorized Terminal Output

The script uses ANSI colors to highlight errors, progress, and success in the terminal, improving the user experience.

### 4. Optional Cleanup

With the `--clean` flag, all temporary files (e.g., `.mol` files, intermediate spectra) are deleted upon script completion, ensuring a clean workspace.

## Dynamic Progress Bars

There are two main progress bars in the script:
1. **Molecular File Generation**: Tracks the process of converting SMILES to `.mol` files.
2. **NMR Prediction**: Displays the progress during the machine learning prediction step for CHI logD.

## Example Outputs

Upon completion, the script will output a CSV file with predicted logD values. The output file will be stored in the `logD_results/` folder, named based on the input CSV file and the model used (e.g., `myfile_1H_query_results.csv`).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
