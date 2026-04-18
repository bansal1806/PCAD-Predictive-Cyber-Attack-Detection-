import os
import sys
import json
import argparse
import pandas as pd

# Ensure the project root is in the path for consistent imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.preprocessing import DataCleaner
from src.feature_engineering import TimeWindowAggregator
from src.models import ModelTrainer
import src.config as config

def main():
    parser = argparse.ArgumentParser(description="Predictive Cyber Attack Detection Pipeline")
    parser.add_argument('--mode', type=str, default='train', choices=['preprocess', 'train', 'serve'], help='Execution mode')
    parser.add_argument('--lstm', action='store_true', help='Also train LSTM model (requires TensorFlow)')
    parser.add_argument('--model', type=str, default=None, help='Specific model to train (e.g. RandomForest, XGBoost, Ensemble)')
    args = parser.parse_args()
    
    if args.mode == 'serve':
        import uvicorn
        print("Starting FastAPI Backend Server...")
        uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
        return

    # Ensure processed directory exists
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)

    # Check if data exists
    if not os.path.exists(config.RAW_DATA_DIR) or not os.listdir(config.RAW_DATA_DIR):
        print(f"CRITICAL ERROR: No data found in {config.RAW_DATA_DIR}")
        print("Please download CIC-IDS 2017 CSVs and place them there.")
        return

    if args.mode == 'preprocess':
        cleaner = DataCleaner()
        aggregator = TimeWindowAggregator(window_size=f'{config.PREDICTION_WINDOW_MINUTES}min')

        # 1. Load & Clean
        raw_files = [
            os.path.join(config.RAW_DATA_DIR, f)
            for f in os.listdir(config.RAW_DATA_DIR)
            if f.endswith('.csv')
        ]
        print(f"Found {len(raw_files)} CSV files.")

        df = cleaner.run_pipeline(raw_files)

        # 2. Aggregate into time windows
        agg_df = aggregator.aggregate_flows(df)
        agg_df = aggregator.create_prediction_target(agg_df, lookahead_steps=1)

        # 3. Save
        output_path = os.path.join(config.PROCESSED_DATA_DIR, 'aggregated_data.csv')
        agg_df.to_csv(output_path)
        print(f"\nPreprocessed data saved to {output_path}")
        print(f"Final shape: {agg_df.shape}")

    elif args.mode == 'train':
        # 1. Load Processed
        data_path = os.path.join(config.PROCESSED_DATA_DIR, 'aggregated_data.csv')
        if not os.path.exists(data_path):
            print("Processed data not found. Run --mode preprocess first.")
            return

        df = pd.read_csv(data_path, index_col=0)  # Index is Timestamp
        print(f"Loaded processed data: {df.shape}")

        trainer = ModelTrainer()

        # 2. Split
        X_train, y_train, X_test, y_test = trainer.train_test_split_time(df)

        # 3. Train models
        results = trainer.train_models(X_train, y_train, X_test, y_test, selected_model=args.model)

        # 4. Update metrics.json
        metrics_path = os.path.join(trainer.output_dir, 'metrics.json')
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                metrics_out = json.load(f)
        else:
            metrics_out = {}

        for name, res in results.items():
            metrics_out[name] = {
                'ROC_AUC': round(res['ROC_AUC'], 4),
                'F1_Score': round(res['F1_Score'], 4),
            }
        
        with open(metrics_path, 'w') as f:
            json.dump(metrics_out, f, indent=2)
        print(f"\nMetrics updated in {metrics_path}")

        # 5. XAI: SHAP Explainability (bonus points)
        if 'XGBoost' in results:
            trainer.explain_model_shap(results['XGBoost']['Model'], X_test, model_name='XGBoost')

        # 6. Optional LSTM (run with --lstm flag)
        if args.lstm:
            print("\n--- Training LSTM (Bonus Algorithm) ---")
            lstm_result = trainer.train_lstm(X_train, y_train, X_test, y_test)
            if lstm_result:
                metrics_out['LSTM'] = {
                    'ROC_AUC': round(lstm_result['ROC_AUC'], 4),
                    'F1_Score': round(lstm_result['F1_Score'], 4),
                }
                with open(metrics_path, 'w') as f:
                    json.dump(metrics_out, f, indent=2)
                print("LSTM metrics saved.")

        print("\n=== Training Complete ===")
        print("Model comparison:")
        for name, m in metrics_out.items():
            print(f"  {name:20s} → ROC-AUC: {m['ROC_AUC']:.4f}  F1: {m['F1_Score']:.4f}")

if __name__ == "__main__":
    main()
