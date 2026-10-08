import joblib

model = joblib.load("../models/best_model.pkl")

print("MODEL TYPE:")
print(type(model))

print("\nMODEL:")
print(model)

if hasattr(model, "n_features_in_"):
    print("\nNUMBER OF FEATURES:")
    print(model.n_features_in_)

if hasattr(model, "feature_names_in_"):
    print("\nFEATURE NAMES:")
    print(model.feature_names_in_)

if hasattr(model, "classes_"):
    print("\nCLASSES:")
    print(model.classes_)