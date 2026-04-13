# --- CONTRIBUTOR 2: DATA, DEEP LEARNING & API SERVING ---
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
import joblib
import pickle
import random
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

# Load security environment
load_dotenv()
PCAD_API_KEY = os.getenv("PCAD_API_KEY", "pcad-secure-2024")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Setup Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="PCAD API", description="Predictive Cyber Attack Detection API", version="1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup Audit Logging
os.makedirs('logs', exist_ok=True)
from logging.handlers import RotatingFileHandler
audit_handler = RotatingFileHandler('logs/security_audit.log', maxBytes=10**6, backupCount=5)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[audit_handler, logging.StreamHandler()]
)
audit_logger = logging.getLogger("PCAD_Audit")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == PCAD_API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Invalid or Missing API Key")

# CORS Restriction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Global variables for models
models = {}
scaler = None
live_data = None
attack_data = None
current_idx = 0
simulation_mode = False
simulation_end_time = 0
current_attack_type = None
MODEL_DIR = 'models'

class TrafficData(BaseModel):
    # flexible input for now since exact features depend on dataset
    features: Dict[str, float]

class SimulationRequest(BaseModel):
    n_samples: int = 10

@app.on_event("startup")
def load_artifacts():
    global models, scaler, live_data, attack_data
    print("Loading models...")
    model_files = {
        'LinearModel': 'LinearModel.pkl',
        'LogisticRegression': 'LogisticRegression.pkl',
        'SVM': 'SVM.pkl',
        'RandomForest': 'RandomForest.pkl',
        'XGBoost': 'XGBoost.pkl',
        'Ensemble': 'Ensemble.pkl'
    }
    
    try:
        if os.path.exists(os.path.join(MODEL_DIR, 'scaler.joblib')):
            scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.joblib'))
    except Exception as e:
        print(f"Could not load scaler: {e}")

    for name, filename in model_files.items():
        path = os.path.join(MODEL_DIR, filename)
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    models[name] = pickle.load(f)
                print(f"Loaded {name}")
            except Exception as e:
                print(f"Failed to load {name}: {e}")
        else:
            print(f"Model {name} not found at {path}. Ignoring.")
            
    # Load live data for simulation
    try:
        data_path = os.path.join('data', 'processed', 'aggregated_data.csv')
        if os.path.exists(data_path):
            live_data = pd.read_csv(data_path)
            attack_data = live_data[live_data['target'] == 1].copy() if 'target' in live_data.columns else None
            print(f"Loaded live data for simulation: {len(live_data)} rows")
    except Exception as e:
        print(f"Could not load live data: {e}")

@app.get("/status")
def get_status():
    return {
        "status": "online",
        "loaded_models": list(models.keys()),
        "scaler_loaded": scaler is not None
    }

@app.post("/predict")
async def predict(request: Request, data: TrafficData, api_key: str = Depends(get_api_key)):
    if not models:
        raise HTTPException(status_code=503, detail="No models loaded")
    
    # Convert input to DataFrame/Array
    # NOTE: This assumes 'features' keys match training columns exactly. 
    # For MVP we handle a simplified list or specific known keys.
    # Since we don't have the dataset yet, we'll assume a list of values if keys are not specific
    
    try:
        # Convert dictionary to DataFrame
        input_data = pd.DataFrame([data.features])
        
        # Scale if scaler exists
        if scaler:
            # Ensure columns match what scaler expects
            if hasattr(scaler, 'feature_names_in_'):
                expected_cols = scaler.feature_names_in_
                # Reorder and fill missing with zeros
                for c in expected_cols:
                    if c not in input_data.columns:
                        input_data[c] = 0
                input_data = input_data[expected_cols]
            
            input_array = scaler.transform(input_data)
        else:
            input_array = input_data.values

        results = {}
        
        # Use Ensemble if available, else best single model
        model_to_use = models.get('Ensemble') or models.get('RandomForest') or list(models.values())[0]
        model_name = 'Ensemble' if 'Ensemble' in models else type(model_to_use).__name__
        
        prediction = model_to_use.predict(input_array)[0]
        
        # Probabilities
        if hasattr(model_to_use, 'predict_proba'):
            prob = model_to_use.predict_proba(input_array)[0][1] # P(Attack)
        else:
            prob = float(prediction)

        if prediction == 1:
            if simulation_mode and current_attack_type:
                attack_type = current_attack_type
            else:
                attack_type = "Unknown Anomaly (Zero-Day?)"
        else:
            attack_type = "None"

        response = {
            "prediction": int(prediction),
            "probability": float(prob),
            "model_used": model_name,
            "status": "Attack Detected" if prediction == 1 else "Normal Traffic",
            "attack_type": attack_type
        }
        
        # Log critical detections
        if prediction == 1:
            audit_logger.warning(f"THREAT DETECTED: Model={model_name}, Prob={prob:.4f}, Features={data.features}")
        
        return response
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/metrics")
def get_metrics():
    """Returns real training metrics from the saved metrics.json file."""
    metrics_path = os.path.join(MODEL_DIR, 'metrics.json')
    if os.path.exists(metrics_path):
        import json
        with open(metrics_path, 'r') as f:
            all_metrics = json.load(f)
        # Return best model (Ensemble) as primary, full breakdown included
        best = all_metrics.get('Ensemble', all_metrics.get('RandomForest', {}))
        return {
            "roc_auc": best.get('ROC_AUC', 0.0),
            "f1_score": best.get('F1_Score', 0.0),
            "all_models": all_metrics
        }
    # Fallback if models not trained yet
    return {
        "roc_auc": None,
        "f1_score": None,
        "message": "Models not trained yet. Run: python main.py --mode train"
    }

@app.get("/comparison")
def get_model_comparison():
    """Returns all model metrics for frontend comparison chart."""
    metrics_path = os.path.join(MODEL_DIR, 'metrics.json')
    if os.path.exists(metrics_path):
        import json
        with open(metrics_path, 'r') as f:
            return json.load(f)
    return {}


@app.post("/simulate-attack")
async def simulate_attack(api_key: str = Depends(get_api_key)):
    """Activates sustained attack simulation for 30 seconds."""
    global simulation_mode, simulation_end_time, current_attack_type
    simulation_mode = True
    simulation_end_time = time.time() + 30 # 30 seconds of sustained attack
    current_attack_type = random.choice(["DDoS (Syn Flood)", "Brute Force (SSH)", "Port Scan", "Botnet C&C", "Data Exfiltration"])
    audit_logger.warning(f"VIVA DEMO: Manual attack trigger activated. Sustained attack mode engaged. Type: {current_attack_type}")
    return {"status": "success", "message": "Attack simulation active", "attack_type": current_attack_type}

@app.get("/live-traffic")
async def get_live_traffic(request: Request, batch_size: int = 1, api_key: str = Depends(get_api_key)):
    """Returns real traffic data from the test set sequentially."""
    global current_idx, live_data, attack_data, simulation_mode, simulation_end_time
    if live_data is None or len(live_data) == 0:
        return []
        
    if simulation_mode and time.time() > simulation_end_time:
        simulation_mode = False
    
    if simulation_mode and attack_data is not None and not attack_data.empty:
        batch = attack_data.sample(n=batch_size).copy()
        # Add random jitter to metrics to look realistic
        batch['Total Fwd Packets_sum'] = batch['Total Fwd Packets_sum'] * random.uniform(1.2, 2.5)
        batch['Flow Duration_mean'] = batch['Flow Duration_mean'] * random.uniform(1.5, 3.0)
    else:
        if current_idx >= len(live_data):
            current_idx = 0 # loop back
            
        end_idx = min(current_idx + batch_size, len(live_data))
        batch = live_data.iloc[current_idx:end_idx].copy()
        current_idx = end_idx
    
    records = batch.to_dict(orient='records')
    results = []
    
    for r in records:
        # Separate features from meta-columns
        features = {k: v for k, v in r.items() if k not in ['target', 'Timestamp']}
        
        # Map raw features to visualization fields for the dashboard
        # Fallback to random if these specific features aren't present
        packet_size = r.get('Total Fwd Packets_sum', random.uniform(100, 1000))
        latency = r.get('Flow Duration_mean', random.uniform(10, 50))
        
        # Correctly format the timestamp as an ISO string
        raw_ts = r.get('Timestamp', pd.Timestamp.now())
        iso_ts = pd.to_datetime(raw_ts).isoformat()
        
        results.append({
            "timestamp": iso_ts,
            "packet_size": float(packet_size),
            "latency": float(latency),
            "features": features,
            "actual_target": int(r.get('target', 0))
        })
        
    return results
