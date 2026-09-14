# System Architecture

## High-Level Architecture

                 SME NETWORK
                     │
        ┌────────────┼────────────┐
        │            │            │
     Windows       Linux        Web/App
       PCs         Server       Server
        │            │            │
        └────────────┼────────────┘
                     │
                 Wazuh Agents
                     │
                     ▼
              Wazuh Manager
                     │
                     ▼
              Event Ingestion
                     │
                     ▼
             Event Normalization
                     │
                     ▼
             Feature Engineering
                     │
          ┌──────────┴──────────┐
          │                     │
   Wazuh Rule Engine     Isolation Forest
          │                     │
          └──────────┬──────────┘
                     ▼
                Risk Engine
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Alert       Risk      Incident
       Score      Ranking    Grouping
                               │
                               ▼
                     Explainability Layer
                               │
                               ▼
                     Response Orchestrator

Core Components
### 1. Wazuh Manager
Responsible for:
    collecting agent logs
    applying default and custom rules
    generating security alerts

### 2. Ingestion Layer
Receives Wazuh alerts.
Possible methods:
    webhook
    API polling
    syslog
    log file forwarding
    For MVP, webhook is recommended

### 3. Normalization Layer
Converts raw Wazuh JSON alerts into structured events.
Example fields:
    timestamp
    rule_id
    rule_level
    rule_description
    agent_name
    src_ip
    dst_ip
    username
    event_type
    raw_message

### 4. Feature Engineering Layer
Creates numerical features for anomaly detection.
Examples:
    alert_count_5m
    failed_login_count_15m
    unique_srcip_1h
    high_rule_level_count_1h
    off_hours_login_flag
    new_srcip_flag

### 5. Anomaly Detection Layer
Uses Isolation Forest to produce anomaly scores.
Input:
    feature vector

Output:
    anomaly_score
    is_anomaly

### 6. Risk Engine
Combines Wazuh severity and anomaly score.
Output:
    risk_score
    risk_level

### 7. Incident Correlator
Groups related alerts into incidents.
Correlation criteria:
    same source IP
    same user
    same asset
    same time window
    related event sequence
    high risk score

### 8. Explainability Layer
Generates human-readable explanations.
Example:
    Why suspicious?
    - Multiple failed logins detected.
    - Login occurred outside business hours.
    - New source IP observed.
    - High-severity Wazuh rule triggered.

### 9. Response Orchestrator
Recommends or executes response actions.
Actions:
    notify_admin
    block_ip
    isolate_host
    disable_account
    generate_report

Default mode for MVP: dry_run

#### Backend Stack
    Python
    FastAPI
    SQLModel / SQLAlchemy
    PostgreSQL
    Scikit-learn
#### Frontend Stack 
    React
    TypeScript
    Vite
    Ant Design or TailwindCSS
    Recharts
#### Database Table
Initial entities:
    raw_events
    normalized_events
    alerts
    incidents
    response_actions
    sme_profiles
    assets
    audit_logs

#### Security Principles
    Do not automatically execute dangerous actions by default.
    Keep audit logs for every response action.
    Use allowlists for IPs and assets.
    Run attack simulations only in isolated lab environments.
    Store credentials securely.
text```