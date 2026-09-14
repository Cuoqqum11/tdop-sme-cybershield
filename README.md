# SME CyberShield

**Lightweight AI-Assisted XDR for Vietnamese SMEs**

SME CyberShield is a lightweight cybersecurity platform designed to help small and medium-sized enterprises detect, understand, prioritize, and respond to cyber threats without needing a dedicated security team.

The system integrates:

- Wazuh for log collection and rule-based detection
- Python for log normalization and feature engineering
- Isolation Forest for anomaly detection
- A risk engine for alert prioritization
- Incident correlation for grouping related alerts
- Explainable risk scoring
- Response recommendations

## Problem

Vietnamese SMEs are increasingly exposed to cyber threats such as brute-force attacks, suspicious logins, web exploits, account compromise, and ransomware-like behavior. However, many SMEs lack:

- budget for enterprise security tools,
- dedicated cybersecurity staff,
- time to manage complex security systems.

This is the “3U” problem:

- Unaware
- Unfunded
- Uneducated

## Solution

SME CyberShield turns open-source security monitoring into a practical, lightweight XDR platform.

The platform:

1. Collects security events from Wazuh.
2. Normalizes raw alerts into structured events.
3. Extracts behavioral features.
4. Applies Isolation Forest anomaly detection.
5. Combines Wazuh severity and anomaly score into a risk score.
6. Groups related alerts into incidents.
7. Explains why an incident is suspicious.
8. Recommends response actions.

## Core Value

> Cybersecurity that an SME can deploy and operate without a dedicated security department.

## Key Features

- Wazuh alert ingestion
- Event normalization
- Feature engineering
- Isolation Forest anomaly detection
- Risk scoring
- Incident correlation
- Explainable alerts
- Response recommendations
- Local-first deployment
- SME-friendly dashboard

## Tech Stack

- Backend: Python, FastAPI
- Database: PostgreSQL / SQLite for local development
- ML: Scikit-learn, Isolation Forest
- Security: Wazuh
- Frontend: React / TypeScript, planned
- Deployment: Docker Compose

## Repository Structure

```text
backend/        FastAPI backend
ml/             Isolation Forest training and feature engineering
frontend/       Dashboard frontend
docs/           Product and competition documents
simulation/     Lab attack and benign activity scripts
evaluation/     Metrics and ground truth

Quick Start
Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

API docs:
http://localhost:8000/docs

Health check:
http://localhost:8000/health

Docker
docker compose up --build
