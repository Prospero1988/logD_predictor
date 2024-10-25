import torch

def model_predictor(model_path, structure_features):
    # Wczytanie modelu DNN w PyTorch
    model = torch.load(model_path)
    model.eval()  # Ustawienie modelu w tryb ewaluacji, wyłącza dropout i batchnorm

    # Konwersja `structure_features` do tensora PyTorch
    with torch.no_grad():  # Wyłączenie gradientów dla procesu predykcji
        input_features = torch.tensor(structure_features.values, dtype=torch.float32)
        
        # Predykcja przy użyciu modelu
        prediction = model(input_features).numpy()  # Konwersja wyniku do formatu numpy dla kompatybilności
        prediction = prediction.item()
    return prediction
