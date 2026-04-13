# --- CONTRIBUTOR 2: DATA, DEEP LEARNING & API SERVING ---
import pandas as pd
import numpy as np
from scipy.stats import entropy
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.config as config

class TimeWindowAggregator:
    def __init__(self, window_size='5min'):
        self.window_size = window_size

    def calculate_entropy(self, x):
        """Calculates entropy of a distribution (e.g., IP addresses)."""
        counts = x.value_counts()
        return entropy(counts)

    def aggregate_flows(self, df):
        """
        Aggregates flow-based data into time windows.
        
        The CIC-IDS 2017 dataset does NOT have a Timestamp column in the
        MachineLearningCSV version. We reconstruct a synthetic timestamp from
        the 'day_offset' and row order using Flow Duration as an approximation.
        
        Args:
            df: DataFrame with a 'Timestamp' column (synthetic or real).
            
        Returns:
            Aggregated DataFrame with one row per time window.
        """
        print(f"Aggregating data into {self.window_size} windows...")

        if 'Timestamp' not in df.columns:
            raise ValueError("DataFrame must have a 'Timestamp' column. Run preprocessing first.")
        
        # Ensure Timestamp is datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df = df.sort_values('Timestamp').set_index('Timestamp')
        
        # Build aggregation dictionary using actual (stripped) column names
        valid_agg_dict = {}
        if 'Flow Duration' in df.columns:
            valid_agg_dict['Flow Duration'] = ['mean', 'max']
        if 'Total Fwd Packets' in df.columns:
            valid_agg_dict['Total Fwd Packets'] = ['sum']
        if 'Total Backward Packets' in df.columns:
            valid_agg_dict['Total Backward Packets'] = ['sum']
        if 'Flow IAT Mean' in df.columns:
            valid_agg_dict['Flow IAT Mean'] = ['mean']
        if 'Flow Packets/s' in df.columns:
            valid_agg_dict['Flow Packets/s'] = ['mean']

        # Label column for window-level attack labeling
        valid_agg_dict['Label_Binary'] = ['max', 'mean']
        
        agg_df = df.resample(self.window_size).agg(valid_agg_dict)
        
        # Flatten MultiIndex columns
        agg_df.columns = ['_'.join(col).strip() for col in agg_df.columns.values]
        
        # Add Flow Count
        agg_df['flow_count'] = df.resample(self.window_size).size()
        
        # Fill NaNs (empty windows) with 0
        agg_df.fillna(0, inplace=True)

        # --- ADVANCED: Rolling/Lag Features ---
        print("Generating Advanced Rolling Features...")
        features_to_roll = [c for c in agg_df.columns if 'Label' not in c]
        
        for win in [3, 6]:  # Look back 3 and 6 steps (e.g., 15min, 30min)
            for col in features_to_roll:
                agg_df[f'{col}_roll_mean_{win}'] = agg_df[col].rolling(window=win).mean()
                agg_df[f'{col}_roll_std_{win}'] = agg_df[col].rolling(window=win).std()
        
        # Drop NaN created by rolling (first few rows)
        agg_df.dropna(inplace=True)
        
        print(f"Aggregation complete. Output shape: {agg_df.shape}")
        return agg_df

    def create_prediction_target(self, df, lookahead_steps=1):
        """
        Creates the target variable for *Prediction*.
        
        We want to predict if an attack will occur in the NEXT window.
        So we shift the 'Label_Binary_max' column backwards.
        
        Args:
            df: Aggregated DataFrame.
            lookahead_steps: How many windows ahead to predict.
            
        Returns:
            DataFrame with 'target' column.
        """
        target_col = 'Label_Binary_max'
        if target_col not in df.columns:
            candidates = [c for c in df.columns if 'Label' in c and 'max' in c]
            if candidates:
                target_col = candidates[0]
            else:
                raise ValueError("Label column not found in aggregated data.")
        
        df['target'] = df[target_col].shift(-lookahead_steps).fillna(0)
        df['target'] = df['target'].apply(lambda x: 1 if x > 0 else 0)
        
        print(f"Target variable created for {lookahead_steps} steps ahead.")
        return df

if __name__ == "__main__":
    print("TimeWindowAggregator initialized.")
