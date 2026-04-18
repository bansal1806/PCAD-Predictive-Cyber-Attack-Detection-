import pandas as pd
import joblib
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

def test_prediction():
    try:
        df = pd.read_csv('data/processed/aggregated_data.csv')
        row = df.iloc[1240:1241]
        features = row.drop(columns=['target', 'Timestamp'], errors='ignore')
        
        # Load model
        model_path = 'models/Ensemble.pkl'
        if not os.path.exists(model_path):
            print(f"Model not found at {model_path}")
            return
            
        model = joblib.load(model_path)
        
        # Predict
        pred = model.predict(features)
        prob = model.predict_proba(features)
        
        print(f"Index: 1240")
        print(f"Ground Truth (Target): {row['target'].values[0]}")
        print(f"Model Prediction: {pred[0]}")
        print(f"Probabilities: {prob[0]}")
        
        if pred[0] == 0:
            print("WARNING: Model misclassified this attack as benign!")
            # Find an index where the model actually predicts 1
            print("Searching for a row where model predicts 1...")
            # Sample some attack rows
            attack_indices = df[df['target'] == 1].index[:100]
            for idx in attack_indices:
                sample_row = df.iloc[idx:idx+1]
                sample_feats = sample_row.drop(columns=['target', 'Timestamp'], errors='ignore')
                s_pred = model.predict(sample_feats)
                if s_pred[0] == 1:
                    print(f"FOUND! Index {idx} is predicted as ATTACK.")
                    break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_prediction()
