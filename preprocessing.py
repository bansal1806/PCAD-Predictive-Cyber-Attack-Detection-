# --- CONTRIBUTOR 2: DATA, DEEP LEARNING & API SERVING ---
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import sys
import os
import re

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.config as config

# Map CIC-IDS 2017 filenames to actual capture dates
FILE_DATE_MAP = {
    'Monday':    '2017-07-03',
    'Tuesday':   '2017-07-04',
    'Wednesday': '2017-07-05',
    'Thursday':  '2017-07-06',
    'Friday':    '2017-07-07',
}

class DataCleaner:
    def __init__(self):
        self.label_encoder = LabelEncoder()

    def _get_date_for_file(self, filepath):
        """Extracts the weekday from the filename and maps it to a date."""
        basename = os.path.basename(filepath)
        for day, date in FILE_DATE_MAP.items():
            if day.lower() in basename.lower():
                return pd.Timestamp(date)
        # Fallback to epoch if no match
        return pd.Timestamp('2017-07-03')

    def load_data(self, filepath):
        """Loads CSV data and synthesizes a Timestamp column from Flow Duration."""
        print(f"Loading {os.path.basename(filepath)}...")
        try:
            df = pd.read_csv(filepath, encoding='cp1252', low_memory=False)
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
        
        # Strip whitespace from all column names
        df.columns = df.columns.str.strip()
        
        # --- Synthesize Timestamp from file date + cumulative Flow Duration ---
        # Flow Duration is in microseconds. We'll treat rows as sequential flows.
        base_date = self._get_date_for_file(filepath)
        if 'Flow Duration' in df.columns:
            # Cumulative sum of flow durations in microseconds → convert to seconds
            cum_duration_sec = df['Flow Duration'].clip(lower=0).cumsum() / 1_000_000
            df['Timestamp'] = base_date + pd.to_timedelta(cum_duration_sec, unit='s')
        else:
            # Fallback: evenly spaced 1-second intervals
            df['Timestamp'] = pd.date_range(start=base_date, periods=len(df), freq='1s')
        
        return df

    def initial_cleaning(self, df):
        """Removes infinite values and NaNs."""
        print("Cleaning: removing Inf/NaN...")
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        initial_len = len(df)
        df.dropna(inplace=True)
        print(f"  Dropped {initial_len - len(df)} rows containing NaN/Infinity.")
        return df

    def encode_labels(self, df):
        """Encodes 'Label' column to binary (0=Benign, 1=Attack)."""
        if 'Label' not in df.columns:
            print("Warning: 'Label' column not found.")
            return df
        
        df['Label_Binary'] = df['Label'].apply(lambda x: 0 if str(x).strip().upper() == 'BENIGN' else 1)
        dist = df['Label_Binary'].value_counts(normalize=True).to_dict()
        print(f"  Label distribution → Benign: {dist.get(0, 0):.1%}, Attack: {dist.get(1, 0):.1%}")
        
        return df

    def run_pipeline(self, file_paths):
        """Runs the full cleaning pipeline on a list of files."""
        all_dfs = []
        
        for fp in file_paths:
            df = self.load_data(fp)
            if df is not None and len(df) > 0:
                df = self.initial_cleaning(df)
                df = self.encode_labels(df)
                all_dfs.append(df)
                print(f"  → Loaded {len(df):,} rows from {os.path.basename(fp)}")
        
        if not all_dfs:
            raise RuntimeError("No data loaded. Check file paths and CSV structure.")

        full_df = pd.concat(all_dfs, ignore_index=True)
        print(f"\nTotal rows after merge: {len(full_df):,}")
        return full_df

if __name__ == "__main__":
    cleaner = DataCleaner()
    print("DataCleaner initialized.")
