# ML Pipeline

This folder contains the machine learning pipeline for SME CyberShield.

Current planned model:

- Isolation Forest

Pipeline:

1. Export Wazuh logs
2. Normalize events
3. Build features
4. Train Isolation Forest
5. Evaluate anomaly threshold
6. Export model

Future files:

```text
scripts/build_features.py
scripts/train_isolation_forest.py
scripts/evaluate_model.py
configs/isolation_forest.yaml