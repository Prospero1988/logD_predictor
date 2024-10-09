import pandas as pd
import joblib
import os

from logD_predictor_bin.models import model_paths_1H, model_names_1H
from logD_predictor_bin.models import model_paths_13C, model_names_13C

def query(dataset, predictor, verified_csv_path):
    
    # Wybór modelu na podstawie argumentu 'predictor'
    if predictor == '1H':
        model_paths, model_names = model_paths_1H, model_names_1H
    elif predictor == '13C':
        model_paths, model_names = model_paths_13C, model_names_13C
    else:
        raise ValueError("Nieprawidłowy typ predyktora. Dostępne opcje to: '1H' lub '13C'.")
    
    # Tworzenie DataFrame z wejściowego zestawu danych
    df = pd.DataFrame(dataset)

    # Wyodrębnienie cech (od drugiej kolumny)
    features = df.iloc[:, 1:]

    # Inicjalizacja DataFrame do przechowywania wyników
    df2 = df[[df.columns[0]]].copy()  # Skopiowanie pierwszej kolumny z etykietą
    
    for model_path, name in zip(model_paths, model_names):
        
        # Wczytanie modelu za pomocą joblib
        model = joblib.load(model_path)
        
        # Przeprowadzenie predykcji bezpośrednio na danych cech
        predictions = model.predict(features)
        
        # Dodanie predykcji jako nowa kolumna o nazwie modelu w DataFrame
        df2[name] = predictions
    
    # Tworzenie nazwy pliku wynikowego
    new_df_name = os.path.basename(verified_csv_path).split('.')[0] + f"_{predictor}_query_results.csv"
    
    # Zapisanie df do pliku csv
    df2.to_csv(new_df_name, index=False)
    
    # Wyświetlenie dataframe z nową kolumną predykcji
    print(df2)
    
    return df2
