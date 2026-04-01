# --- CONTRIBUTOR 1: ML ENGINE & EXPLAINABILITY ---
import os

# Project Root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data Paths
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
# Kaggle CIC-IDS 2017 dataset (all 8 CSV files extracted here)
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw', 'archive')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')


# Column Definitions for CIC-IDS 2017
# Note: CIC-IDS 2017 feature names often have leading spaces.
numeric_features = [
    ' Flow Duration', ' Total Fwd Packets', ' Total Backward Packets',
    'Total Length of Fwd Packets', ' Total Length of Bwd Packets',
    ' Fwd Packet Length Max', ' Fwd Packet Length Min', ' Fwd Packet Length Mean',
    ' Bwd Packet Length Max', ' Bwd Packet Length Min', ' Bwd Packet Length Mean',
    'Flow Bytes/s', ' Flow Packets/s', ' Flow IAT Mean', ' Flow IAT Std',
    ' Flow IAT Max', ' Flow IAT Min', 'Fwd IAT Total', ' Fwd IAT Mean',
    ' Fwd IAT Std', ' Fwd IAT Max', ' Fwd IAT Min', 'Bwd IAT Total',
    ' Bwd IAT Mean', ' Bwd IAT Std', ' Bwd IAT Max', ' Bwd IAT Min',
    'Fwd PSH Flags', ' Bwd PSH Flags', ' Fwd URG Flags', ' Bwd URG Flags',
    ' Fwd Header Length', ' Bwd Header Length', 'Fwd Packets/s', ' Bwd Packets/s',
    ' Min Packet Length', ' Max Packet Length', ' Packet Length Mean',
    ' Packet Length Std', ' Packet Length Variance', 'FIN Flag Count',
    ' SYN Flag Count', ' RST Flag Count', ' PSH Flag Count', ' ACK Flag Count',
    ' URG Flag Count', ' CWE Flag Count', ' ECE Flag Count', ' Down/Up Ratio',
    ' Average Packet Size', ' Avg Fwd Segment Size', ' Avg Bwd Segment Size',
    ' Fwd Header Length', 'Fwd Avg Bytes/Bulk', ' Fwd Avg Packets/Bulk',
    ' Fwd Avg Bulk Rate', ' Bwd Avg Bytes/Bulk', ' Bwd Avg Packets/Bulk',
    'Bwd Avg Bulk Rate', 'Subflow Fwd Packets', ' Subflow Fwd Bytes',
    ' Subflow Bwd Packets', ' Subflow Bwd Bytes', 'Init_Win_bytes_forward',
    ' Init_Win_bytes_backward', ' act_data_pkt_fwd', ' min_seg_size_forward',
    'Active Mean', ' Active Std', ' Active Max', ' Active Min', 'Idle Mean',
    ' Idle Std', ' Idle Max', ' Idle Min'
]

# Features to Aggregate in Time Windows (stripped column names from actual dataset)
agg_features = {
    'Flow Duration': ['mean', 'max'],
    'Total Fwd Packets': ['sum'],
    'Total Backward Packets': ['sum'],
    'Total Length of Bwd Packets': ['sum'],
    'Flow IAT Mean': ['mean'],
    'Flow Packets/s': ['mean'],
    'Label_Binary': ['max', 'mean'] # Max label in window (1 if any attack, 0 otherwise)
}

# Model Config
RANDOM_SEED = 42
TEST_SIZE = 0.2
LOOKBACK_WINDOW = 5 # Used for LSTM sequence length
PREDICTION_WINDOW_MINUTES = 5
