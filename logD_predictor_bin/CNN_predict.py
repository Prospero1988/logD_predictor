import torch

def model_predictor(model_path, structure_features):
    # Wczytanie modelu CNN w PyTorch
    model = torch.load(model_path, map_location=torch.device('cpu'))
    model.eval()  # Ustawienie modelu w tryb ewaluacji

    # Konwersja `structure_features` do tensora PyTorch o odpowiednich wymiarach
    with torch.no_grad():  # Wyłączenie gradientów dla procesu predykcji
        # Zakładamy, że structure_features to DataFrame lub Series z danymi wejściowymi
        input_features = torch.tensor(structure_features.values, dtype=torch.float32)
        
        # Dopasowanie wymiarów do formatu (1, channels, sequence_length)
        input_features = input_features.unsqueeze(0).unsqueeze(0)  # Dodanie wymiarów batch i channels

        # Predykcja przy użyciu modelu
        prediction = model(input_features).numpy()  # Konwersja wyniku do formatu numpy dla kompatybilności
        prediction = prediction.item()
    return prediction
