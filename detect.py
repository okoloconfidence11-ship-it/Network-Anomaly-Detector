import joblib
import numpy as np
import pandas as pd

try:
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
    print("Model and Scaler loaded successfully.")
except Exception as e:
    print(f"Error loading files: {e}")

def detect_anomaly(sample_data):
    try:
        sample = np.array(sample_data).reshape(1, -1)
        sample_scaled = scaler.transform(sample)
        prediction = model.predict(sample_scaled)
        label = str(prediction[0]).strip().lower()

        if "normal" in label:
            return f"Traffic identified as: {label.upper()}"
        else:
            return f"Suspicious Activity: {label.upper()} detected!"

    except ValueError:
        expected = scaler.n_features_in_
        return f"Input Mismatch: Model expects {expected} features, but got {len(sample_data)}."
    except Exception as e:
        return f"Detection Error: {e}"
    
    def run_test():
        print("\n--- Starting Detection Test ---")
        try:
            num_features = scaler.n_features_in_
            test_input = [0] * num_features
            result = detect_anomaly(test_input)
            print(result)
        except NameError:
            print("Error: Scaler not loaded. Cannot determine feature count.")

    if __name__ == "__main__":
        run_test()