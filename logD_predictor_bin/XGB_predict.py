import joblib
import xgboost as xgb

def model_predictor(model_path, structure_features, quiet):

    # Definiowanie funkcji kontrolującej drukowanie
    def verbose_print(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    # Loading the model using joblib
    model = joblib.load(model_path)
    structure_features = structure_features.astype(float)
    dmatrix_features = xgb.DMatrix(structure_features)
    prediction = model.predict(dmatrix_features)

    return prediction
