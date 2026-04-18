# --- CONTRIBUTOR 1: ML ENGINE & EXPLAINABILITY ---
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
from sklearn.metrics import classification_report, roc_auc_score, f1_score, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
import xgboost as xgb
import pickle
import os
import joblib

class ModelTrainer:
    def __init__(self, output_dir='models'):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.models = self._initialize_models()

    def _initialize_models(self):
        """Initializes base models with default parameters."""
        models = {
            'LinearModel': RidgeClassifier(random_state=42),
            'LogisticRegression': LogisticRegression(max_iter=2000, random_state=42),
            'SVM': LinearSVC(max_iter=5000, random_state=42, dual=False),
            'KNN': KNeighborsClassifier(n_neighbors=5, n_jobs=-1),
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            'XGBoost': xgb.XGBClassifier(eval_metric='logloss', random_state=42, n_jobs=-1)
        }
        return models

    def train_test_split_time(self, df, target_col='target', test_size=0.2):
        """Splits data respecting time order (no shuffling)."""
        # Assume df is already sorted by time (index)
        split_idx = int(len(df) * (1 - test_size))
        
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        X_train = train_df.drop(columns=[target_col])
        y_train = train_df[target_col]
        
        X_test = test_df.drop(columns=[target_col])
        y_test = test_df[target_col]
        
        print(f"Train size: {X_train.shape}, Test size: {X_test.shape}")
        return X_train, y_train, X_test, y_test

    def train_models(self, X_train, y_train, X_test, y_test, selected_model=None):
        results = {}
        
        # Preprocessing Pipeline (Scaling is important for LR and Neural Nets)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Save scaler
        joblib.dump(scaler, os.path.join(self.output_dir, 'scaler.joblib'))

        # Determine which models to train
        models_to_train = {}
        if selected_model:
            if selected_model in self.models:
                models_to_train[selected_model] = self.models[selected_model]
            elif selected_model.lower() == 'ensemble':
                # Special handling for ensemble below
                pass
            else:
                print(f"Error: Model '{selected_model}' not found in initialization.")
                return {}
        else:
            models_to_train = self.models

        for name, model in models_to_train.items():
            print(f"Training {name}...")
            
            # Use scaled data for LR and distance-based models (KNN, SVM, Linear), original for Trees
            scaled_models = ['LogisticRegression', 'KNN', 'SVM', 'LinearModel']
            X_curr_train = X_train_scaled if name in scaled_models else X_train
            X_curr_test = X_test_scaled if name in scaled_models else X_test

            model.fit(X_curr_train, y_train)
            
            y_pred = model.predict(X_curr_test)
            y_prob = model.predict_proba(X_curr_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
            
            # Metrics
            roc = roc_auc_score(y_test, y_prob)
            f1 = f1_score(y_test, y_pred)
            
            results[name] = {
                'ROC_AUC': roc,
                'F1_Score': f1,
                'Model': model
            }
            
            print(f"{name} Results -> ROC: {roc:.4f}, F1: {f1:.4f}")
            
            # Save model
            with open(os.path.join(self.output_dir, f"{name}.pkl"), 'wb') as f:
                pickle.dump(model, f)
        
        # Train Ensemble if requested or if no specific model selected
        if not selected_model or selected_model.lower() == 'ensemble':
            print("Training Ensemble (Soft Voting)...")
            
            pipe_lr = Pipeline([('sc', StandardScaler()), ('clf', LogisticRegression(max_iter=2000, random_state=42))])
            pipe_svm = Pipeline([('sc', StandardScaler()), ('clf', CalibratedClassifierCV(LinearSVC(max_iter=5000, random_state=42, dual=False)))])
            pipe_rf = Pipeline([('clf', RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1))])
            pipe_xgb = Pipeline([('clf', xgb.XGBClassifier(eval_metric='logloss', random_state=42, n_jobs=-1))])
            
            ensemble_refined = VotingClassifier(
                estimators=[('lr', pipe_lr), ('svm', pipe_svm), ('rf', pipe_rf), ('xgb', pipe_xgb)],
                voting='soft'
            )
            ensemble_refined.fit(X_train, y_train)
            
            y_pred_ens = ensemble_refined.predict(X_test)
            y_prob_ens = ensemble_refined.predict_proba(X_test)[:, 1]
            
            results['Ensemble'] = {
                'ROC_AUC': roc_auc_score(y_test, y_prob_ens),
                'F1_Score': f1_score(y_test, y_pred_ens),
                'Model': ensemble_refined
            }
            print(f"Ensemble Results -> ROC: {results['Ensemble']['ROC_AUC']:.4f}")
            
            with open(os.path.join(self.output_dir, "Ensemble.pkl"), 'wb') as f:
                pickle.dump(ensemble_refined, f)

        return results

    def tune_hyperparameters(self, X_train, y_train, model_name='RandomForest'):
        """Performs Randomized Search for hyperparameters."""
        print(f"Tuning {model_name}...")
        
        if model_name == 'RandomForest':
            param_dist = {
                'n_estimators': [100, 200, 300],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10]
            }
            base_model = RandomForestClassifier(random_state=42)
        elif model_name == 'XGBoost':
            param_dist = {
                'learning_rate': [0.01, 0.1, 0.2],
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 5, 7]
            }
            base_model = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
        else:
            print(f"Tuning not implemented for {model_name}.")
            return None
            
        random_search = RandomizedSearchCV(
            base_model, 
            param_distributions=param_dist, 
            n_iter=5, 
            cv=3, 
            scoring='roc_auc', 
            n_jobs=-1, 
            random_state=42
        )
        random_search.fit(X_train, y_train)
        
        print(f"Best params for {model_name}: {random_search.best_params_}")
        return random_search.best_estimator_

    def explain_model_shap(self, model, X_test, model_name='XGBoost'):
        """
        Generates SHAP summary plot for the model.
        Requires 'shap' library to be installed.
        """
        try:
            import shap
            import matplotlib.pyplot as plt
            
            print(f"Generating SHAP plots for {model_name}...")
            
            # Handle Pipeline objects (extract classifier)
            if isinstance(model, Pipeline):
                model_to_explain = model.named_steps['clf']
                # Note: SHAP on pipeline might need transformed data
                # For simplicity here, we skip pipeline unwrap logic for SHAP in MVP
                print("SHAP for Pipelines is complex to visualize automatically. Skipping.")
                return 

            # Create object that can calculate shap values
            if model_name in ['XGBoost', 'RandomForest']:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X_test)
                
                # Plot
                plt.figure()
                shap.summary_plot(shap_values, X_test, show=False)
                plt.savefig(os.path.join(self.output_dir, f'{model_name}_shap_summary.png'))
                plt.close()
                print("SHAP Summary plot saved.")
            else:
                print("SHAP explanation not implemented for this model type.")
                
        except ImportError:
            print("SHAP library not installed. Skipping explanation.")
        except Exception as e:
            print(f"Error generating SHAP values: {e}")

    def build_lstm_model(self, input_shape):
        """Builds a simple LSTM model using Keras."""
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            
            print("Building LSTM Model...")
            model = Sequential()
            model.add(LSTM(64, return_sequences=True, input_shape=input_shape))
            model.add(Dropout(0.3))
            model.add(LSTM(32))
            model.add(Dropout(0.3))
            model.add(Dense(16, activation='relu'))
            model.add(Dense(1, activation='sigmoid'))
            
            model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
            return model
        except ImportError:
            print("TensorFlow/Keras not installed. Please install 'tensorflow'.")
            return None

    def prepare_sequences(self, X, y, window_size=5):
        """
        Converts 2D tabular data into 3D sequences for LSTM.
        Shape: (Samples, Timesteps, Features)
        """
        X_seq, y_seq = [], []
        for i in range(len(X) - window_size):
            X_seq.append(X.iloc[i : (i + window_size)].values)
            y_seq.append(y.iloc[i + window_size])
            
        return np.array(X_seq), np.array(y_seq)

    def train_lstm(self, X_train, y_train, X_test, y_test):
        """Processes sequences and trains the LSTM model."""
        import os
        
        # Scaling is required for LSTM
        scaler = StandardScaler()
        X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
        X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
        
        # Prepare sequences
        window = 5 # Default 5-step lookback
        X_train_3d, y_train_3d = self.prepare_sequences(X_train_scaled, y_train, window_size=window)
        X_test_3d, y_test_3d = self.prepare_sequences(X_test_scaled, y_test, window_size=window)
        
        model = self.build_lstm_model((X_train_3d.shape[1], X_train_3d.shape[2]))
        
        if model:
            print("Training LSTM (this may take a while)...")
            model.fit(
                X_train_3d, y_train_3d, 
                epochs=10, 
                batch_size=32, 
                validation_split=0.1, 
                verbose=1
            )
            
            # Save Keras model
            model.save(os.path.join(self.output_dir, 'LSTM.h5'))
            print(f"LSTM model saved to {self.output_dir}/LSTM.h5")
            
            # Evaluate
            loss, acc = model.evaluate(X_test_3d, y_test_3d)
            y_prob = model.predict(X_test_3d)
            y_pred = (y_prob > 0.5).astype(int)
            
            f1 = f1_score(y_test_3d, y_pred)
            roc = roc_auc_score(y_test_3d, y_prob)
            
            print(f"LSTM Results -> ROC: {roc:.4f}, F1: {f1:.4f}")
            return {'ROC_AUC': roc, 'F1_Score': f1, 'Model': model}
        
        return None

if __name__ == "__main__":
    print("ModelTrainer initialized.")
