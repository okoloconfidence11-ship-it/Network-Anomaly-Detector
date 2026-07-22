from fastapi import FastAPI
import joblib
import numpy as np
from pydantic import BaseModel
from typing import List
from sklearn.preprocessing import StandardScaler
import uvicorn
import tensorflow as tf
from tensorflow.keras import layers, models

def build_cnn(num_features, num_classes):
    model = models.Sequential([
        layers.Input(shape=(num_features, 1)),
        layers.Conv1D(32, kernel_size=3, activation='relu'),
        layers.MaxPooling1D(pool_size=2),
        layers.Conv1D(64, kernel_size=3, activation='relu'),
        layers.GlobalAveragePooling1D(),
        layers.Dense(64, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def proffer_remedy(label):
    knowledge_base = {
        "NORMAL": {
            "reasoning": "Traffic patterns match standard baseline behavior.",
            "fix": "No action required."
        },
        "DoS": {
            "reasoning": "High packet frequency detected on a single port.",
            "fix": "Apply rate-limiting: sudo iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute"
        },
        "Probe": {
            "reasoning": "Sequential scanning of closed ports identified.",
            "fix": "Enable IPS/IDS and block the source IP immediately using fail2ban."
        },
        "Unknown": {
            "reasoning": "The AI detected a pattern that doesn't match known signatures.",
            "fix": "sudo ufw default deny incoming && sudo ufw allow from [INTERNAL_IP]"
        }
    }
    return knowledge_base.get(label, {
        "reasoning": "Atypical traffic detected.",
        "fix": "Monitor network logs for unusual IP behavior."
    })

app = FastAPI(title="Network Anomaly Detection API")

model = tf.keras.models.load_model("model.h5")
scaler = joblib.load("scaler.pkl")

class NetworkData(BaseModel):
    features: List[float]

@app.get("/")
def home():
    return {"message": "Network Guard API is Online"}

@app.post("/predict")
def predict(data: NetworkData):
    try:
        input_data = np.array(data.features).reshape(1, -1)
        scaled_data = scaler.transform(input_data)
        
        num_features = scaled_data.shape[1]
        reshaped_data = scaled_data.reshape(1, num_features, 1)
        
        prediction_probs = model.predict(reshaped_data)
        prediction_code = np.argmax(prediction_probs, axis=1)[0]
        
        mapping = {0: "NORMAL", 1: "DoS", 2: "Probe"}
        label = mapping.get(prediction_code, "Unknown")
        
        if label == "NORMAL":
            status = "SAFE"
        else:
            status = "ALERT"
            
        remedy = proffer_remedy(label)
        
        return {
            "status": status,
            "prediction": label,
            "message": f"Traffic analyzed as {label}",
            "explanation": remedy.get("reasoning"),
            "fix": remedy.get("fix")
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)