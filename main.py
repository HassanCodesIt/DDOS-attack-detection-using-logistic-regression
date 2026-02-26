"""
DDoS Attack Detection — FastAPI server.

Endpoints:
  GET  /          → serves the frontend (static/index.html)
  GET  /health    → health-check
  POST /predict   → classify a single network-traffic sample
"""

from __future__ import annotations

import logging
import os
import warnings

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="DDoS Attack Detection API",
    description="Logistic-Regression model that classifies network traffic as Normal or DDoS.",
    version="1.0.0",
)

# Serve everything in static/ under /static (used by the HTML page)
static_dir = os.path.join(BASE_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
MODEL_PATH = os.path.join(BASE_DIR, "ddos_logistic_regression.pkl")
model = joblib.load(MODEL_PATH)

# The model was trained on 55 features produced by:
#   X = df.drop(columns=['dt', 'label'])
#   X = pd.get_dummies(X, drop_first=True)
# The feature names below match that preprocessing on the SDN dataset.
FEATURE_NAMES: list[str] = [
    "switch",
    "src",
    "dst",
    "pktcount",
    "bytecount",
    "dur",
    "dur_nsec",
    "tot_dur",
    "flows",
    "packetins",
    "pktperflow",
    "byteperflow",
    "pktrate",
    "Pkt_Rx",
    "Pkt_Tx",
    "Pkt_drp_Rx",
    "Pkt_drp_Tx",
    "Pkt_err",
    "Bytes_Rx",
    "Bytes_Tx",
    "Pkts_Rx_Drp",
    "Bytes_Rx_Drp",
    "tot_kbps",
    "pktloss",
    "tx_kbps",
    "rx_kbps",
    "port_no",
    "Protocol_ICMP",
    "Protocol_TCP",
    "Protocol_UDP",
]

# Pad with generic names to reach the model's expected 55 features
_padded = model.n_features_in_ - len(FEATURE_NAMES)
if _padded > 0:
    logger.warning(
        "FEATURE_NAMES has %d entries but model expects %d. "
        "Padding with %d generic feature name(s). "
        "Update FEATURE_NAMES in main.py to match the training feature set.",
        len(FEATURE_NAMES),
        model.n_features_in_,
        _padded,
    )
while len(FEATURE_NAMES) < model.n_features_in_:
    FEATURE_NAMES.append(f"feature_{len(FEATURE_NAMES)}")

assert len(FEATURE_NAMES) == model.n_features_in_, (
    f"Expected {model.n_features_in_} features, got {len(FEATURE_NAMES)}"
)

LABEL_MAP = {0: "Normal Traffic", 1: "DDoS Attack"}


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class TrafficSample(BaseModel):
    """Network-traffic features for a single observation."""

    switch: float = Field(default=1, description="Switch identifier")
    src: float = Field(default=0, description="Source node / IP (numeric)")
    dst: float = Field(default=0, description="Destination node / IP (numeric)")
    pktcount: float = Field(default=0, description="Total packet count")
    bytecount: float = Field(default=0, description="Total byte count")
    dur: float = Field(default=0, description="Flow duration (seconds)")
    dur_nsec: float = Field(default=0, description="Flow duration (nanoseconds part)")
    tot_dur: float = Field(default=0, description="Total flow duration")
    flows: float = Field(default=0, description="Number of flows")
    packetins: float = Field(default=0, description="Packet-in messages to controller")
    pktperflow: float = Field(default=0, description="Packets per flow")
    byteperflow: float = Field(default=0, description="Bytes per flow")
    pktrate: float = Field(default=0, description="Packet rate (packets/second)")
    Pkt_Rx: float = Field(default=0, description="Packets received")
    Pkt_Tx: float = Field(default=0, description="Packets transmitted")
    Pkt_drp_Rx: float = Field(default=0, description="Receive-side packet drops")
    Pkt_drp_Tx: float = Field(default=0, description="Transmit-side packet drops")
    Pkt_err: float = Field(default=0, description="Packet errors")
    Bytes_Rx: float = Field(default=0, description="Bytes received")
    Bytes_Tx: float = Field(default=0, description="Bytes transmitted")
    Pkts_Rx_Drp: float = Field(default=0, description="Received packets dropped")
    Bytes_Rx_Drp: float = Field(default=0, description="Received bytes dropped")
    tot_kbps: float = Field(default=0, description="Total throughput (kbps)")
    pktloss: float = Field(default=0, description="Packet loss")
    tx_kbps: float = Field(default=0, description="Transmit throughput (kbps)")
    rx_kbps: float = Field(default=0, description="Receive throughput (kbps)")
    port_no: float = Field(default=0, description="Port number")
    Protocol_ICMP: int = Field(default=0, description="1 if Protocol is ICMP else 0")
    Protocol_TCP: int = Field(default=0, description="1 if Protocol is TCP else 0")
    Protocol_UDP: int = Field(default=0, description="1 if Protocol is UDP else 0")


class PredictionResult(BaseModel):
    prediction: int
    label: str
    confidence: float
    probabilities: dict[str, float]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _build_feature_vector(sample: TrafficSample) -> np.ndarray:
    """Convert a TrafficSample into the numpy array expected by the model."""
    sample_dict = sample.model_dump()
    df_row = pd.DataFrame([sample_dict])

    # Add any missing expected features with 0
    for col in FEATURE_NAMES:
        if col not in df_row.columns:
            df_row[col] = 0.0

    # Align to the exact column order the model was trained with
    df_row = df_row[FEATURE_NAMES]
    return df_row.to_numpy(dtype=float)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=FileResponse, include_in_schema=False)
def serve_frontend():
    """Serve the HTML/JS frontend."""
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/health", tags=["utility"])
def health():
    """Simple health-check endpoint."""
    return {"status": "ok", "model_features": model.n_features_in_}


@app.post("/predict", response_model=PredictionResult, tags=["detection"])
def predict(sample: TrafficSample):
    """
    Classify a network-traffic sample as Normal Traffic or a DDoS Attack.

    Returns the predicted class, a human-readable label, and the model's
    confidence score (probability of the predicted class).
    """
    feature_vector = _build_feature_vector(sample)
    prediction: int = int(model.predict(feature_vector)[0])
    proba: np.ndarray = model.predict_proba(feature_vector)[0]

    return PredictionResult(
        prediction=prediction,
        label=LABEL_MAP[prediction],
        confidence=round(float(proba[prediction]), 4),
        probabilities={
            "Normal Traffic": round(float(proba[0]), 4),
            "DDoS Attack": round(float(proba[1]), 4),
        },
    )
