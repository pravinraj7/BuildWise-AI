"""
BuildWise AI — ML Training Pipeline
Trains XGBoost failure predictor + Isolation Forest anomaly detector
"""
import os
import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)


def train_failure_predictor():
    """Train XGBoost equipment failure predictor."""
    print("🏋️ Training Failure Predictor (XGBoost)...")

    # Load or generate training data
    data_path = Path("../datasets/equipment_features.csv")
    if data_path.exists():
        df = pd.read_csv(data_path)
    else:
        # Generate synthetic training data
        n = 1000
        np.random.seed(42)
        df = pd.DataFrame({
            "age_days": np.random.randint(30, 3650, n),
            "days_since_maintenance": np.random.randint(0, 500, n),
            "maintenance_count": np.random.randint(0, 20, n),
            "total_maintenance_cost": np.random.uniform(0, 50000, n),
            "avg_repair_duration": np.random.uniform(0.5, 10, n),
            "current_health_score": np.random.uniform(20, 100, n),
            "is_critical": np.random.randint(0, 2, n),
            "equipment_type_encoded": np.random.randint(0, 8, n),
            "failure_probability": np.random.beta(2, 5, n),
        })
        df["failed"] = (df["failure_probability"] > 0.6).astype(int)

    # Features and target
    features = ["age_days", "days_since_maintenance", "maintenance_count",
                "total_maintenance_cost", "avg_repair_duration", "current_health_score",
                "is_critical", "equipment_type_encoded"]
    
    if "failed" not in df.columns:
        df["failed"] = (df.get("failure_probability", 0.5) > 0.5).astype(int)

    # Filter to available features
    available = [f for f in features if f in df.columns]
    X = df[available].fillna(0)
    y = df["failed"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    try:
        import xgboost as xgb
        model = xgb.XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8,
            use_label_encoder=False, eval_metric="auc",
            random_state=42, verbosity=0,
        )
        model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_proba)
        
        joblib.dump(model, MODELS_DIR / "failure_predictor_generic.joblib")
        print(f"   ✅ XGBoost saved — AUC: {auc:.3f}")
        print(f"\n{classification_report(y_test, y_pred)}")
    except ImportError:
        print("   ⚠️ XGBoost not available, trying LightGBM...")
        try:
            import lightgbm as lgb
            model = lgb.LGBMClassifier(n_estimators=200, random_state=42, verbosity=-1)
            model.fit(X_train, y_train)
            joblib.dump(model, MODELS_DIR / "failure_predictor_generic.joblib")
            print("   ✅ LightGBM model saved")
        except ImportError:
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            joblib.dump(model, MODELS_DIR / "failure_predictor_generic.joblib")
            print("   ✅ RandomForest fallback saved")


def train_anomaly_detector():
    """Train Isolation Forest for anomaly detection."""
    print("🔍 Training Anomaly Detector (Isolation Forest)...")
    from sklearn.ensemble import IsolationForest
    import numpy as np

    # Generate normal operational data
    np.random.seed(42)
    n = 800
    normal_data = np.column_stack([
        np.random.normal(200, 50, n),   # age (normal range)
        np.random.normal(30, 10, n),    # days since maintenance
        np.random.normal(85, 10, n),    # health score (good)
        np.random.normal(2, 0.5, n),    # maintenance count
    ])

    model = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
    model.fit(normal_data)
    
    joblib.dump(model, MODELS_DIR / "anomaly_detector.joblib")
    print("   ✅ Isolation Forest saved")


def train_cost_estimator():
    """Train Random Forest for cost estimation."""
    print("💰 Training Cost Estimator (Random Forest)...")
    from sklearn.ensemble import RandomForestRegressor
    import numpy as np

    np.random.seed(42)
    n = 500
    X = np.column_stack([
        np.random.choice([0, 1, 2, 3, 4], n),  # category encoded
        np.random.uniform(0.5, 8, n),           # duration hours
        np.random.choice([0, 1, 2, 3, 4], n),  # priority encoded
        np.random.uniform(0, 100, n),            # health score
    ])
    y = 500 + X[:, 1] * 600 + X[:, 2] * 500 + np.random.normal(0, 300, n)
    y = np.maximum(y, 200)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    score = model.score(X_test, y_test)
    joblib.dump(model, MODELS_DIR / "cost_estimator.joblib")
    print(f"   ✅ Random Forest saved — R²: {score:.3f}")


if __name__ == "__main__":
    print("🚀 BuildWise AI — ML Training Pipeline\n")
    train_failure_predictor()
    print()
    train_anomaly_detector()
    print()
    train_cost_estimator()
    print("\n✅ All models trained and saved to ml/models/")
