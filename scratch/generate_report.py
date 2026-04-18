import pandas as pd
import numpy as np
import os
import joblib
import pickle
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score, f1_score, recall_score, precision_score, accuracy_score
import sys

# Ensure project root is in path
sys.path.insert(0, os.getcwd())

from src.models import ModelTrainer

def generate_report():
    trainer = ModelTrainer()
    output_dir = 'models'
    data_path = 'data/processed/aggregated_data.csv'
    
    if not os.path.exists(data_path):
        print(f"Data not found at {data_path}")
        return

    # 1. Load and Split Data
    df = pd.read_csv(data_path, index_col=0)
    X_train, y_train, X_test, y_test = trainer.train_test_split_time(df)
    
    # 2. Load Scaler
    scaler = joblib.load(os.path.join(output_dir, 'scaler.joblib'))
    X_test_scaled_flat = scaler.transform(X_test)
    X_test_scaled_df = pd.DataFrame(X_test_scaled_flat, columns=X_test.columns)
    
    model_names = ['LinearModel', 'LogisticRegression', 'SVM', 'KNN', 'RandomForest', 'XGBoost', 'Ensemble']
    scaled_models = ['LogisticRegression', 'KNN', 'SVM', 'LinearModel']
    
    results = []
    plt.figure(figsize=(10, 8))
    
    # --- Tabular Models ---
    for name in model_names:
        path = os.path.join(output_dir, f"{name}.pkl")
        if not os.path.exists(path):
            continue
            
        with open(path, 'rb') as f:
            model = pickle.load(f)
            
        X_curr = X_test_scaled_flat if name in scaled_models else X_test
        y_pred = model.predict(X_curr)
        
        if hasattr(model, 'predict_proba'):
            y_prob = model.predict_proba(X_curr)[:, 1]
        elif hasattr(model, 'decision_function'):
            y_prob = model.decision_function(X_curr)
        else:
            y_prob = y_pred
            
        acc = accuracy_score(y_test, y_pred)
        roc = roc_auc_score(y_test, y_prob)
        f1 = f1_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        
        results.append({
            'Model': name,
            'Accuracy': f"{acc:.4f}",
            'ROC AUC': f"{roc:.4f}",
            'F1 Score': f"{f1:.4f}",
            'Recall': f"{recall:.4f}",
            'Precision': f"{precision:.4f}"
        })
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        plt.plot(fpr, tpr, label=f'{name} (AUC = {roc:.4f})')

    # --- LSTM Model (Special Handling) ---
    lstm_path = os.path.join(output_dir, 'LSTM.h5')
    if os.path.exists(lstm_path):
        try:
            from tensorflow.keras.models import load_model
            model = load_model(lstm_path)
            
            # Sequence Preparation
            window = 5
            X_test_3d, y_test_3d = trainer.prepare_sequences(X_test_scaled_df, y_test, window_size=window)
            
            y_prob_lstm = model.predict(X_test_3d)
            y_pred_lstm = (y_prob_lstm > 0.5).astype(int)
            
            acc = accuracy_score(y_test_3d, y_pred_lstm)
            roc = roc_auc_score(y_test_3d, y_prob_lstm)
            f1 = f1_score(y_test_3d, y_pred_lstm)
            recall = recall_score(y_test_3d, y_pred_lstm)
            precision = precision_score(y_test_3d, y_pred_lstm)
            
            results.append({
                'Model': 'LSTM',
                'Accuracy': f"{acc:.4f}",
                'ROC AUC': f"{roc:.4f}",
                'F1 Score': f"{f1:.4f}",
                'Recall': f"{recall:.4f}",
                'Precision': f"{precision:.4f}"
            })
            fpr, tpr, _ = roc_curve(y_test_3d, y_prob_lstm)
            plt.plot(fpr, tpr, label=f'LSTM (AUC = {roc:.4f})')
            print("LSTM evaluated successfully.")
        except Exception as e:
            print(f"Error evaluating LSTM: {e}")

    # Finalize Plot
    plt.plot([0, 1], [0, 1], 'k--', label='Random')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves - All PCAD Models')
    plt.legend(loc='lower right')
    plt.grid(alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'roc_curves_all.png'))
    plt.close()
    
    # Print Table
    print("\n### Complete Model Comparison Table\n")
    headers = ['Model', 'Accuracy', 'ROC AUC', 'F1 Score', 'Recall', 'Precision']
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join(["---"] * len(headers)) + " |")
    for res in results:
        print("| " + " | ".join([res[h] for h in headers]) + " |")

if __name__ == "__main__":
    generate_report()
