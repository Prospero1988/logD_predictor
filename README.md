
# logD Predictor

**logD Predictor** is a graphical application for the prediction of the **CHI logD** parameter based on machine learning (ML) and deep learning models trained on **¹H and ¹³C NMR spectral representations**. Additionally, it supports predictions based on **RDKit-generated molecular fingerprints**.  

The tool is built entirely in **Python** and integrates a graphical user interface (GUI) for both installation and usage. It incorporates the core functionality of the [Demiurge](https://github.com/Prospero1988/Demiurge) pipeline, with additional layers for model selection, prediction, and result visualization. All models used in the application were trained on datasets containing over 1,200 compounds and underwent full hyperparameter optimization using **Optuna**.

## 💡 Key Features
- Spectral-based prediction using theoretical ¹H and ¹³C NMR vectors
- Optional prediction from RDKit molecular fingerprints
- GUI-based interaction with multiple input/output and configuration options
- Multi-model ensemble predictions and averaging
- Automatic chart generation and model performance logging

---

## 🗂 Repository Structure

```
logD_predictor/
│
├── logD_predictor_bin/           # Main execution directory
│   ├── img/                      # Icons and GUI-related images
│   ├── joblib_models/            # (To be copied manually after download from SourceForge)
│   ├── predictor/                # Java-based predictor for ¹H and ¹³C NMR spectra
│   ├── *.py                      # Python backend scripts
│
├── Prediction_Results/          # Directory for output logs and charts
│
├── INSTALL.pyw                  # GUI-based script for Python module installation
├── START.pyw                    # GUI launcher for logD Predictor
├── README.md                    # This file
├── RUN_LOG_FILE.log             # Internal log file for debugging
```

---

## ⚙️ Installation

### ✅ Option 1: Native Python (Recommended for Windows 11)

1. Double-click `INSTALL.pyw` – it will automatically install all required Python packages.
2. Install **Java SDK** (tested on version 23); ensure `java` and `javac` are available in PATH.
3. Download the model package:  
   [joblib_models.rar](https://sourceforge.net/projects/logdpredictor/files/joblib_models.rar/download)  
   - Unpack the archive and place the `joblib_models` folder inside `logD_predictor_bin/`.

> ✅ Tested on Python 3.12 and Windows 11.

---

### ✅ Option 2: Conda Environment

1. Create a new environment and install packages using the provided `install_text.txt`:
   ```bash
   conda create -n logd_env python=3.12
   conda activate logd_env
   pip install -r install_text.txt
   ```
2. Install Java SDK (as above) and copy the `joblib_models` folder to the correct location.

---

## 🚀 Running the Application

- **Native Python**: Just double-click `START.pyw`
- **Conda**: Open terminal, activate environment and run:
  ```bash
  python START.pyw
  ```

This will launch the **GUI interface** of logD Predictor.

---

## 📄 Input File Format

You can start by clicking **"Open Input File Example"** from the GUI to view the required input format.  
Alternatively, use **"Select with Input Example"** to load a prepared test file.

📌 Input must be a CSV file with valid **SMILES** strings and appropriate headers.  
**Do not delete or alter the column headers.**

---

## 🧪 Prediction Options (via GUI)

### Select Representation
Choose the type of input data to base your prediction on:
- **Proton** (¹H NMR)
- **Carbon** (¹³C NMR)
- **RDKit FP** (fingerprints)
- **All Above** (ensemble)

### Available Models
Select one or more models to use for prediction. If multiple are selected, predictions are averaged.

### Script Execution Options
The following options are available:
- **Quiet mode**: suppress detailed output (default: ON)
- **Debug mode**: save temporary files and logs
- **Show models**: display full model metrics (RMSE, MAE, etc.)
- **Generate charts**: display prediction charts

> 🖼 For a preview of the interface:  
> `logD_predictor_bin/img/IMG/logD_predictor_GUI.png`

---

## 🔗 Related Projects

- [Demiurge (NMR processing backend)](https://github.com/Prospero1988/Demiurge)
- [Main NMR-AI Project](https://github.com/Prospero1988/NMR-AI_part3)

---

## 📜 License

This project is released under the **MIT License**.  
All scripts and models are provided **free of charge** for academic and non-commercial use.
