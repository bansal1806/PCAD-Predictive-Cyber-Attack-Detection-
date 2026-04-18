# Predictive Cyber Attack Detection (PCAD)

End-to-end Machine Learning project for predicting cyber attacks using network traffic data.
**Course**: CS1138
**Status**: Week 5 (Proposal & Planning)

## Project Structure
- `data/`: Contains raw and processed datasets.
    - `raw/`: Place your CIC-IDS 2017 CSV files here.
    - `processed/`: Output of the aggregation pipeline.
- `src/`: Source code modules.
    - `config.py`: Configuration settings.
    - `preprocessing.py`: Data cleaning and cleaning.
    - `feature_engineering.py`: Time-window aggregation logic (Key Innovation).
    - `models.py`: Training logic for LR, RF, XGBoost.
- `docs/`: Deliverables.
    - `project_proposal.md`: Problem statement and methodology.
    - `literature_review.md`: Comparison of 15 research papers.

## Setup
1. Install dependencies:
   ```bash
   C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe -m pip install --upgrade pip
   ```
2. Download Data:
   - Download "CIC-IDS 2017" (CSV version).
   - Place the CSV files in `data/raw/`.

## Usage
### 1. Preprocessing & Aggregation
Run this to convert raw flow data into time-windowed predictive datasets:
```bash
python main.py --mode preprocess
```

### 2. Model Training
Train and evaluate the models:
```bash
python main.py --mode train
```

## Methodology
The project shifts from *detection* to *prediction* by aggregating traffic indices into 5-minute windows and training models to predict the probability of an attack in the *next* window.

### Key Advanced Features:
- **Temporal/Rolling Features**: Uses Exponential Weighted Moving Averages (EWMA) and Rolling Standard Deviations to capture traffic trends and "burstiness" over time.
- **Explainable AI (XAI)**: Integrates **SHAP (SHapley Additive exPlanations)** to provide deep insights into feature importance, moving beyond "black box" predictions.
- **Deep Learning Ready**: Includes skeleton for **LSTM** (Long Short-Term Memory) networks for sequence-based anomaly prediction.
