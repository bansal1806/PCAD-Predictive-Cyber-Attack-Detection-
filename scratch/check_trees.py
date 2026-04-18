import pickle
import os
import xgboost as xgb

def check_tree_counts():
    output_dir = 'models'
    
    # 1. Random Forest
    rf_path = os.path.join(output_dir, 'RandomForest.pkl')
    if os.path.exists(rf_path):
        with open(rf_path, 'rb') as f:
            rf_model = pickle.load(f)
            print(f"RandomForest: {len(rf_model.estimators_)} trees")
    
    # 2. XGBoost
    xgb_path = os.path.join(output_dir, 'XGBoost.pkl')
    if os.path.exists(xgb_path):
        with open(xgb_path, 'rb') as f:
            xgb_model = pickle.load(f)
            # Try getting booster info
            try:
                booster = xgb_model.get_booster()
                num_boost_rounds = len(booster.get_dump())
                print(f"XGBoost: {num_boost_rounds} boosting rounds (trees)")
            except:
                params = xgb_model.get_params()
                print(f"XGBoost: {params.get('n_estimators', 'Default (100)')} trees (from params)")

if __name__ == "__main__":
    check_tree_counts()
