import math
from pathlib import Path
from typing import Any, Dict, Optional

import joblib

from app.services.feature_extractor import FEATURE_COLUMNS


MODEL_PATH = (
    Path(__file__).resolve().parents[3]
    / "ml"
    / "models"
    / "isolation_forest.joblib"
)

_model = None


def load_model():
    """
    Load Isolation Forest model from ml/models/isolation_forest.joblib.

    The model is loaded once and cached in memory.
    """
    global _model

    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)

    return _model


def score_feature_vector(features: Dict[str, Any]) -> Optional[float]:
    """
    Score a feature vector using Isolation Forest.

    Returns:
        float between 0 and 1, where higher means more anomalous.
        None if model is not available.
    """
    model = load_model()

    if model is None:
        return None

    try:
        x = [
            [
                float(features.get(column, 0.0))
                for column in FEATURE_COLUMNS
            ]
        ]

        raw_score = float(model.score_samples(x)[0])

        # Isolation Forest score_samples:
        # lower / more negative = more anomalous
        # higher / more positive = more normal
        #
        # Convert to 0..1 anomaly score using sigmoid-like transformation.

        if raw_score > 50:
            return 0.0

        if raw_score < -50:
            return 1.0

        anomaly_score = 1.0 / (1.0 + math.exp(raw_score))

        return max(0.0, min(1.0, anomaly_score))

    except Exception:
        return None