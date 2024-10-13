import pandas as pd
import joblib
import os

def query(dataset, predictor, verified_csv_path, show_models_table = False):
    
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
    required_columns = ['model_path', 'model_name']
    for col in required_columns:
        if col not in model_table_df.columns:
            raise ValueError(f'{COLORS[1]}Error: Column "{col}" does not exist in DataFrame. Check your {model_table_path} file.{RESET}')
            return None
        if not pd.api.types.is_string_dtype(model_table_df[col]):
            raise ValueError(f'{COLORS[1]}Error: Column "{col}" is not of type string. Check you model data: {model_table_path}{RESET}')
            return None
        
    columns_to_round = ['RMSE', 'MAE', 'R2', 'PEARSON']
    for col in columns_to_round:
        if pd.api.types.is_numeric_dtype(model_table_df[col]):
            model_table_df[col] = model_table_df[col].round(4)
        else:
            print(f"\n{COLORS[1]}Error: Column '{col}' is not numeric, it cannot be rounded.{RESET}")
    
    model_table_df = model_table_df.sort_values(by='model_name').reset_index(drop=True)
    
    # Creating a DataFrame from the input dataset
    df = pd.DataFrame(dataset)
    
    # Extracting features (from the second column onward)
    features = df.iloc[:, 1:]

    # Initializing a DataFrame to store results
    df2 = df[[df.columns[0]]].copy()  # Copying the first column with the label

    try:
        # Iterating over rows in the model_table_df instead of creating lists
        for index, row in model_table_df.iterrows():
            model_path = row['model_path']
            model_name = row['model_name']
            
            # Loading the model using joblib
            model = joblib.load(model_path)
            
            # Making predictions directly on the feature data
            predictions = model.predict(features)
            
            # Adding predictions as a new column named after the model in the DataFrame
            df2[model_name] = predictions.round(2)
    
    except Exception as e:
        print(f"{COLORS[1]}An error occurred: {e}{RESET}")
    
    # Creating the name for the result file
    new_df_name = os.path.basename(verified_csv_path).split('.')[0] + f"_{predictor}_query_results.csv"
    
    # Saving the df to a CSV file
    ultimate_dir = os.path.join(os.getcwd(), f'{predictor}_logD_results')
    if not os.path.exists(ultimate_dir):
        print(f"\n{COLORS[2]}{ultimate_dir}{RESET} directory has been created.")
        os.makedirs(ultimate_dir, exist_ok=True)
    
    new_df_filepath = os.path.join(ultimate_dir, new_df_name)
    
    df2.to_csv(new_df_filepath, index=False)
    
    # Calculating the length of the first message line
    first_line = f"Prediction results for {COLORS[2]}CHI logD{RESET} using ML models based on theoretical {COLORS[0]}{predictor}{RESET} spectra from the NMRshiftDB2 database.{RESET}"
    first_line_raw = "Prediction results for CHI logD using ML models based on theoretical 13C spectra from the NMRshiftDB2 database."
    line_length = len(first_line_raw)
    second_line = f'\n{COLORS[0]}The CSV file with the prediction results is saved as: \n{new_df_name} \nin the folder {ultimate_dir}{RESET}'

    # Printing the results with dynamic plus sign lines
    print("\n" + "+" * line_length)
    print(first_line)
    print("+" * line_length + "\n")
    print(df2)
    print("\n" + "+" * line_length)
    print(second_line)

    print(f"\nOption {COLORS[2]}--models{RESET} has been selected. The script will display below a table"
          f" with details and training metrics for the ML models used.\n")
    
    df_show_models = model_table_df.copy()
    df_show_models = df_show_models.drop('model_path', axis=1)
    df_show_models[['model_name', 'ML_algorithm', 'dataset']] = df_show_models[['model_name', 'ML_algorithm', 'dataset']].astype('string')
    
    # Force alignment for text columns only
    df_show_models[df_show_models.select_dtypes(include=['object']).columns] = df_show_models.select_dtypes(include=['object']).astype(str)
    print(df_show_models.to_string(justify='left'))


    print('')

    return df2
