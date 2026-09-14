# Product Specification: SME CyberShield

## 1. Product Name

SME CyberShield

## 2. One-Line Description

A lightweight AI-assisted XDR platform that helps Vietnamese SMEs detect, understand, and respond to cyber threats without needing a dedicated security team.

## 3. Problem Statement

Vietnamese SMEs are increasingly targeted by cyber threats such as brute-force attacks, suspicious logins, web exploits, account compromise, and ransomware-like behavior.

However, SMEs often face the “3U” problem:

- Unaware of cybersecurity risks
- Unfunded, with limited budget for enterprise security tools
- Uneducated, with limited technical expertise to operate complex systems

Existing enterprise security platforms are often too expensive, too complex, and too difficult for SMEs to operate.

## 4. Target Users

Primary users:

- Vietnamese SMEs with 1–100 computers
- Small IT staff or no dedicated cybersecurity team
- Businesses handling customer data, invoices, accounting records, or personal data

Example target segments:

- accounting firms,
- clinics,
- retail businesses,
- education centers,
- small manufacturing companies,
- professional service companies.

## 5. Product Promise

SME CyberShield provides:

> Continuous security monitoring, understandable alerts, prioritized incidents, and practical response recommendations at a cost suitable for SMEs.

## 6. Core Product Modules

### 6.1 Wazuh Integration

The system receives security alerts from Wazuh.

Sources may include:

- endpoint logs,
- authentication logs,
- web server logs,
- system logs,
- file integrity events.

### 6.2 Event Normalization

Raw Wazuh JSON alerts are converted into structured normalized events.

Examples of normalized fields:

- timestamp,
- rule ID,
- rule level,
- rule description,
- agent name,
- source IP,
- destination IP,
- username,
- event type.

### 6.3 Feature Engineering

The system extracts behavioral features such as:

- number of alerts in a time window,
- failed login frequency,
- source IP frequency,
- unusual hour activity,
- high-severity alert count,
- new source IP flag,
- abnormal event type frequency.

### 6.4 Anomaly Detection

The system uses Isolation Forest to assign anomaly scores to events.

Isolation Forest is suitable because it is:

- lightweight,
- efficient,
- unsupervised,
- appropriate for anomaly detection in tabular data.

### 6.5 Risk Engine

The risk engine combines:

- Wazuh rule severity,
- anomaly score,
- asset criticality,
- repeated suspicious activity.

Initial simplified formula:

risk_score = normalized_wazuh_severity

Later on our risk_score will become 
risk_score =
      0.45 * wazuh_severity
    + 0.40 * anomaly_score
    + 0.10 * asset_criticality
    + 0.05 * repeat_frequency
with the risk score ranging from 0-100

Risk levels:
    0–39   Low
    40–69  Medium
    70–89  High
    90–100 Critical

### 6.6 Incident Correlation

    Multiple failed logins
        ↓
    Successful login
        ↓
    Suspicious process execution
        ↓
    Abnormal file access
        ↓
    High-risk incident

### 6.7 Explainability

Risk: 87/100

Why?
- Multiple failed login attempts detected.
- Successful login occurred after repeated failures.
- Login occurred outside normal business hours.
- Source IP has not been observed before.
- Abnormal file access activity detected.

Recommended action:
- Reset account credentials.
- Isolate affected endpoint.
- Review recent file activity.

### 6.8 Response Recommendations

The system can recommend or safely execute response actions.

Examples:
    notify administrator,
    block source IP,
    disable compromised account,
    isolate endpoint,
    generate incident report.


for MVP, the response actions right now is set default to dry run, which means the system records what it would do, but does not automatically perform risky actions

## 7. Success Metrics
Technical metrics:
    -detection rate
    -false positive rate
    -precision
    -recall
    -F1-score
    -mean time to detect
    -mean time to respond
    -alert reduction rate
Product metrics:
    -number of raw alerts grouped into incidents
    -average risk score
    -time from attack simulation to incident creation
    -dashboard usability
    -administrator understanding of alerts

In general, we are expanding from the research to a structure of something like this:
    -a working backend
    -a dashboard
    -incident grouping
    -explainability
    -response recommendations
    -SME-focused onboarding
    -commercialization path

```text
