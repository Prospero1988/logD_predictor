import joblib
#import warnings

#tymczasowe wygaszenie powiadomień z ostrzeżeniami. Docelowo muszą zostać, żeby nie było problemó z wersją bibliotek
#warnings.filterwarnings("ignore", message=".*Trying to unpickle estimator.*")

def model_predictor(model_path, structure_features, quiet):

    # Definiowanie funkcji kontrolującej drukowanie
    def verbose_print(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    # Loading the model using joblib
    model = joblib.load(model_path)
    structure_features = structure_features.astype(float)
    prediction = model.predict(structure_features.values)

    return prediction