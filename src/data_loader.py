# --- CONTRIBUTOR 2: DATA, DEEP LEARNING & API SERVING ---
import pandas as pd
import numpy as np

class DataLoader:
    def __init__(self, data_path='data'):
        self.data_path = data_path
        
    def load_csv(self, filename):
        """Robust CSV loader with error handling."""
        try:
            path = f"{self.data_path}/{filename}"
            print(f"Loading {path}...")
            df = pd.read_csv(path)
            print(f"Loaded data with shape: {df.shape}")
            return df
        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
            return None
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None
            
    def clean_data(self, df):
        """Basic cleaning pipeline."""
        if df is None:
            return None
            
        # Drop duplicates
        df = df.drop_duplicates()
        
        # Handle missing values (simple imputation for now)
        # For numeric, fill with mean. For categorical, mode or 'Unknown'
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns
        
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        for col in categorical_cols:
            df[col] = df[col].fillna(df[col].mode()[0])
            
        return df

    def get_dummy_data(self, n_rows=1000):
        """Generates dummy data for testing the pipeline without dataset."""
        print("Generating dummy data...")
        # Create random features
        data = {
            'feature_1': np.random.normal(0, 1, n_rows),
            'feature_2': np.random.beta(0.5, 0.5, n_rows),
            'packet_len': np.random.randint(50, 1500, n_rows),
            'ttl': np.random.randint(10, 128, n_rows),
            'target': np.random.randint(0, 2, n_rows) # Binary classification
        }
        return pd.DataFrame(data)
