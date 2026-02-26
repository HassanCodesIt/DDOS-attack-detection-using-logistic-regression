"""
FastAPI endpoint for DDoS Attack Detection using Logistic Regression.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="DDoS Attack Detection API",
    description="A machine learning API to detect DDoS attacks using Logistic Regression",
    version="1.0.0"
)

# Load the trained model
MODEL_PATH = Path(__file__).parent / "ddos_logistic_regression.pkl"

try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print(f"Warning: Model file not found at {MODEL_PATH}")

# Define expected feature names (based on original training script)
# These are the core numeric features from the SDN dataset
FEATURE_NAMES = [
    "pktcount", "bytecount", "dur", "dur_nsec", "tot_dur",
    "flows", "packetins", "pktperflow", "byteperflow", "pktrate",
    "Pairflow", "port_no", "tx_bytes", "rx_bytes", "tx_kbps",
    "rx_kbps", "tot_kbps", "Protocol_ICMP", "Protocol_TCP", "Protocol_UDP"
]

# The model was trained with one-hot encoded features (src, dst, switch, etc.)
# resulting in 55 total features
MODEL_FEATURE_COUNT = 55


class NetworkTrafficInput(BaseModel):
    """
    Input schema for network traffic data.
    """
    pktcount: float = 0
    bytecount: float = 0
    dur: float = 0
    dur_nsec: float = 0
    tot_dur: float = 0
    flows: float = 0
    packetins: float = 0
    pktperflow: float = 0
    byteperflow: float = 0
    pktrate: float = 0
    Pairflow: float = 0
    port_no: float = 0
    tx_bytes: float = 0
    rx_bytes: float = 0
    tx_kbps: float = 0
    rx_kbps: float = 0
    tot_kbps: float = 0
    Protocol_ICMP: float = 0
    Protocol_TCP: float = 0
    Protocol_UDP: float = 0


class PredictionResponse(BaseModel):
    """
    Response schema for prediction results.
    """
    prediction: int
    label: str
    confidence: str


def format_input(sample_dict: dict) -> np.ndarray:
    """
    Converts a dictionary of sample features into a NumPy array matching model input.
    The model expects 55 features (20 core features + 35 one-hot encoded columns for
    categorical data like IP addresses). We use the 20 core features and pad with
    zeros for the remaining 35 features.
    """
    # Create array with correct feature count, initialized to 0
    result = np.zeros((1, MODEL_FEATURE_COUNT))

    # Fill in the core features in order
    for i, col in enumerate(FEATURE_NAMES):
        if col in sample_dict and i < MODEL_FEATURE_COUNT:
            result[0, i] = float(sample_dict[col])

    return result


@app.get("/")
async def root():
    """
    Serve the frontend HTML page.
    """
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(traffic_data: NetworkTrafficInput):
    """
    Predict whether the network traffic is a DDoS attack.

    Args:
        traffic_data: Network traffic features

    Returns:
        Prediction result with label (0 = Normal, 1 = DDoS Attack)
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Convert Pydantic model to dictionary
    sample_dict = traffic_data.model_dump()

    # Format input for the model
    sample_input = format_input(sample_dict)

    # Make prediction
    predicted_label = int(model.predict(sample_input)[0])

    # Get prediction probabilities if available
    try:
        probabilities = model.predict_proba(sample_input)[0]
        confidence = f"{probabilities[predicted_label] * 100:.2f}%"
    except AttributeError:
        confidence = "N/A"

    # Map labels
    label_map = {0: "Normal Traffic", 1: "DDoS Attack Detected"}

    return PredictionResponse(
        prediction=predicted_label,
        label=label_map[predicted_label],
        confidence=confidence
    )


# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=static_path), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
