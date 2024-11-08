import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import sys
import subprocess

# W głównym skrypcie
from SVR_predict import model_predictor as SVR_predictor
from XGB_predict import model_predictor as XGB_predictor
from DNN_predict import model_predictor as DNN_predictor
from CNN_predict import model_predictor as CNN_predictor

def query(dataset, predictor, show_models_table=False, quiet=False, chart=False, use_svr=False, use_xgb=False, use_dnn=False, use_cnn=False):
    
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
    
    model_table_file = f"{predictor}_models_info.csv"
    model_table_path = os.path.join(os.getcwd(), "logD_predictor_bin", "joblib_models", model_table_file)
    
    if not os.path.exists(model_table_path):
        print(f"{COLORS[1]}File {model_table_path} does not exist. Check your data and add relevant model files and data. {RESET}")
        return None
    
    model_table_df = pd.read_csv(model_table_path, sep=';', decimal='.')
    
    # Checking that the 'model_path' and 'model_name' columns exist and are of string type
    required_columns = ['model_path', 'model_name', 'ML_algorithm', 'property']
    for col in required_columns:
        if col not in model_table_df.columns:
            raise ValueError(f'{COLORS[1]}Error: Column "{col}" does not exist in DataFrame. Check your {model_table_path} file.{RESET}')
            return None
        if not pd.api.types.is_string_dtype(model_table_df[col]):
            raise ValueError(f'{COLORS[1]}Error: Column "{col}" is not of type string. Check your model data: {model_table_path}{RESET}')
            return None
    
    columns_to_round = ['RMSE', 'MAE', 'R2', 'PEARSON']
    for col in columns_to_round:
        if pd.api.types.is_numeric_dtype(model_table_df[col]):
            model_table_df[col] = model_table_df[col].round(4)
        else:
            print(f"\n{COLORS[1]}Error: Column '{col}' is not numeric, it cannot be rounded.{RESET}")
        
    # Create directory for saving results
    ultimate_dir = os.path.join(os.getcwd(), "Prediction_Results", f'{predictor}_logD_results')
    if not os.path.exists(ultimate_dir):
        print(f"\n{COLORS[2]}{ultimate_dir}{RESET} directory has been created.")
        os.makedirs(ultimate_dir, exist_ok=True)

    # Słownik predyktorów
    origin_predictor_dict = {
        "SVR": SVR_predictor,
        "XGB": XGB_predictor,
        "DNN": DNN_predictor,
        "CNN": CNN_predictor
    }
    
    # Filtracja słownika na podstawie przekazanych argumentów
    predictor_dict = {}
    if use_svr:
        predictor_dict["SVR"] = origin_predictor_dict["SVR"]
    if use_xgb:
        predictor_dict["XGB"] = origin_predictor_dict["XGB"]
    if use_dnn:
        predictor_dict["DNN"] = origin_predictor_dict["DNN"]
    if use_cnn:
        predictor_dict["CNN"] = origin_predictor_dict["CNN"]
    
    # Informacja o aktywnych modelach
    if not predictor_dict:
        print("No predictors selected. Please enable at least one predictor (e.g., use_svr=True).")
        return None

    # **Nowa część kodu: filtracja model_table_df**
    # Filtrujemy model_table_df, aby zawierał tylko modele z ML_algorithm, które są w predictor_dict
    model_table_df = model_table_df[model_table_df['ML_algorithm'].isin(predictor_dict.keys())]

    # Sprawdzenie, czy po filtracji model_table_df nie jest pusty
    if model_table_df.empty:
        print(f"{COLORS[1]}No models available for the selected predictors.{RESET}")
        return None

    # Reszta kodu pozostaje bez zmian
    # Tworzenie dynamic_dfs na podstawie przefiltrowanego model_table_df
    dynamic_dfs = {}

    # Iterating over unique values in 'property' to create dynamic DataFrames
    for prop_value in model_table_df['property'].unique():
        filtered_df = model_table_df[model_table_df['property'] == prop_value]
        df_name = f"df_{prop_value}"
        dynamic_dfs[df_name] = filtered_df

    # Initialize an empty list to collect results
    summary_data = []

    # Initialize a set to keep track of all properties
    all_properties = set()
    
    # Loading dataset containing columns 'MOLECULE_NAME' and 'FEATURES'
    df = pd.DataFrame(dataset)
    
    # Iterating over each row in the dataset
    for index, structure in df.iterrows():
        molecule_name = str(structure[structure.index[0]])
        structure_features = structure.iloc[1:].to_frame().T

        # Initialize a dictionary to store results for this molecule
        molecule_data = {'MOLECULE_NAME': molecule_name}

        # Looping through each 'property' DataFrame in dynamic_dfs
        for df_name in dynamic_dfs:
            # Resetting structure_result at the start of each iteration for a new df_name
            structure_result = pd.DataFrame({structure.index[0]: [structure[structure.index[0]]]})

            for idx, row in dynamic_dfs[df_name].iterrows():
                model_path = row['model_path']
                model_name = row['model_name']
                prop_value = row['property']
                ml_algorithm = row['ML_algorithm']
                model_path = os.path.join(os.getcwd(),"logD_predictor_bin", "joblib_models", model_path)
                
                model_predictor = predictor_dict[ml_algorithm]
                predicted_value = round(float(model_predictor(model_path, structure_features, quiet)), 2)

                structure_result[model_name] = predicted_value

            # Collect the property
            all_properties.add(prop_value)

            # Calculate average and standard deviation of all models for the current property
            average_value = round(structure_result.iloc[0, 1:].mean(), 2)
            std_value = round(structure_result.iloc[0, 1:].std(), 2)

            # Add the average and standard deviation to structure_result
            structure_result_with_average = structure_result.copy()
            structure_result_with_average['Average'] = average_value
            structure_result_with_average['StdDev'] = std_value

            # Save results
            structure_result_path = os.path.join(ultimate_dir, f'{molecule_name}_{prop_value}.csv')
            structure_result_with_average.to_csv(structure_result_path, index=False, sep=';')
            
            verbose_print(f'Property: {COLORS[2]}{prop_value}{RESET} Molecule: {COLORS[2]}{molecule_name}{RESET}')
            verbose_print(structure_result.to_string(index=False))
            verbose_print(f'\n   Average value: {COLORS[0]}{average_value}{RESET}')
            verbose_print(f'   Standard Deviation: {COLORS[0]}{std_value}{RESET}')
            verbose_print('-----------------------------')
            
            # Collect data for summary with string keys
            molecule_data[f'{prop_value}_Average'] = average_value
            molecule_data[f'{prop_value}_StdDev'] = std_value

        # Append molecule data to summary_data
        summary_data.append(molecule_data)

    # After processing all molecules, create summary_results DataFrame
    summary_results = pd.DataFrame(summary_data)

    # Process columns to create MultiIndex
    columns = []
    for col in summary_results.columns:
        if col == 'MOLECULE_NAME':
            columns.append(('MOLECULE_NAME', ''))
        else:
            prop, stat = col.rsplit('_', 1)
            columns.append((prop, stat))

    # Set the columns as MultiIndex
    summary_results.columns = pd.MultiIndex.from_tuples(columns)

    # Reorder columns if desired
    # Define the desired order of properties
    desired_properties = ['CHI_logD_pH_2.6', 'CHI_logD_pH_7.4', 'CHI_logD_pH_10.5']

    # Create the list of desired columns
    columns = [('MOLECULE_NAME', '')]
    for prop in desired_properties:
        columns.append((prop, 'Average'))
        columns.append((prop, 'StdDev'))

    # Reindex the DataFrame
    summary_results = summary_results.reindex(columns=columns)

    # Display or save summary results

    print(f"\n{COLORS[2]}------------------------------------------{RESET}")
    print(f"Summary Average Results for All Molecules")
    if predictor in ['1H', '13C']:
        print(f"Predicted on {COLORS[2]}{predictor} NMR {RESET}ML Models")
    if predictor == 'FP':
        print(f"Predicted on {COLORS[2]}RDKit Fingerprints{RESET} ML Models")
    print(f"{COLORS[2]}------------------------------------------\n{RESET}")
    print(summary_results.to_string(index=False))
    summary_results.to_csv(os.path.join(ultimate_dir, f"summary_results_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"), sep=';')
    print(f'\nResults files saved in {COLORS[2]}{ultimate_dir}{RESET}\n')

    if show_models_table:
        print(f"Option {COLORS[2]}--models{RESET} has not been selected. The script will display below a table"
              f" with details and training metrics for the ML models used.\n")
        
        df_show_models = model_table_df.copy()
        df_show_models = df_show_models.drop('model_path', axis=1)
        df_show_models[['model_name', 'ML_algorithm', 'property']] = df_show_models[['model_name', 'ML_algorithm', 'property']].astype('string')
        print(df_show_models)
        print('\n\n')

    # Lista kolorów dla wykresów
    colors = ['red', 'green', 'blue']

    if chart:

        # Generowanie wykresów
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.subplots_adjust(wspace=0.2)  # Ustawienie wspace

        for i, (ax, prop, color) in enumerate(zip(axes, desired_properties, colors)):
            # Pobierz dane dla danego property
            x = summary_results['MOLECULE_NAME']
            y = summary_results[(prop, 'Average')]
            yerr = summary_results[(prop, 'StdDev')]

            # Wykres punktowy z "wąsami" błędu
            ax.errorbar(x, y, yerr=yerr, fmt='o', capsize=5, color=color, ecolor='black')
            ax.set_title(prop, fontweight='bold')
            ax.set_xlabel('Molecule name/ID', fontweight='bold')
            ax.set_ylabel('Average logD values', fontweight='bold')

            # Ustawienia formatu liczby na osi Y
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}'))

            # Obróć etykiety osi X, jeśli to konieczne
            ax.tick_params(axis='x', rotation=90)

        fig.suptitle(f"Average logD values from {predictor} representation Predictor", fontweight='bold', fontsize=16)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        # Zapisz wykres
        chart_file_path = os.path.join(ultimate_dir, 'summary_results_plot.png')
        plt.savefig(chart_file_path)

        print(f"Plot saved as {chart_file_path}")
            
        # Otwórz zapisany obrazek w domyślnym programie do przeglądania obrazów
        try:
            if sys.platform.startswith('win'):
                # Windows
                os.startfile(chart_file_path)
            elif sys.platform.startswith('linux'):
                # Linux
                subprocess.call(['xdg-open', chart_file_path])
            elif sys.platform.startswith('darwin'):
                # macOS
                subprocess.call(['open', chart_file_path])
            else:
                print("Unsupported operating system. Cannot open the image automatically.")
        except Exception as e:
            print(f"Could not open image file: {e}")

