# MVP Scope

## Must-Have Features

### 1. Wazuh Alert Ingestion

The backend can receive Wazuh alerts.

Endpoint:
POST /api/v1/wazuh/webhook

### 2. Event Normalization
Raw alerts are converted into normalized events.

### 3. Simple Risk Score
Initial riosk score based on Wazuh rule level.
Example:
    risk_score = rule_level * 10

### 4. Alert Storage
High-severity alerts are stored in the database.

### 5. Basic API:
Endpoints:
    GET /health
    GET /api/v1/alerts
    GET /api/v1/incidents
    GET /api/v1/dashboard/summary

### 6. Isolation Forest Prototype
Train a basic Isolation Forest model using extracted features.

### 7. Incident Grouping
Group related alerts into incidents.

### 8. Simple Dashboard
Display:
    total alerts,
    active incidents,
    risk overview,
    incident details.

### 9. Demo Scenario
We will try to go for at least one working demo before the deadline end:

    Brute force login
        ↓
    Suspicious login
        ↓
    High risk incident

### 10. Evaluation Report
Compare:
    Wazuh-only detection
    vs
    Wazuh + Isolation Forest

## Nice-to-Have Features
    automated IP blocking
    host isolation
    Vietnamese UI
    SME onboarding wizard
    PDF incident report
    Telegram/email notification
    compliance-oriented report

## Out of Scope for MVP
    full enterprise SOC platform,
    full EDR agent development,
    advanced malware reverse engineering,
    production-grade multi-tenant SaaS,
    legal compliance certification.
    
```text
