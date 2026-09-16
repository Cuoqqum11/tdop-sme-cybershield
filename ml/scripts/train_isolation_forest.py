import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

repo_root = Path(__file__).resolve().parents[2]
backend_path = repo_root / "backend"

if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.services.feature_extractor import FEATURE_COLUMNS


def main():
    input_path = repo_root / "ml" / "data" / "processed" / "features.csv"

    if not input_path.exists():
        raise SystemExit(
            "features.csv not found. Run ml/scripts/build_features.py first."
        )

    df = pd.read_csv(input_path)

    if df.empty:
        raise SystemExit("No feature rows found in features.csv.")

    X = df[FEATURE_COLUMNS].fillna(0)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
    )

    model.fit(X)

    model_path = repo_root / "ml" / "models" / "isolation_forest.joblib"
    model_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, model_path)

    print(f"Trained Isolation Forest on {len(X)} feature rows.")
    print(f"Model saved to {model_path}")


if __name__ == "__main__":
    main()