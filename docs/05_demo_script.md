# Demo Script

## Demo Goal

Show judges that SME CyberShield can:

1. receive security events,
2. detect suspicious behavior,
3. create a risk-scored incident,
4. explain why it is suspicious,
5. recommend a response action.

## 5-Minute Demo

### Minute 0–1: Problem

Say:

> Vietnamese SMEs cannot afford or operate complex cybersecurity systems. SME CyberShield turns open-source security monitoring into a simple, lightweight XDR platform.

### Minute 1–2: Dashboard

Show:
    System status: Normal
    Active incidents: 0
    Risk level: Low

### Minute 2–3: Simulated Attack

Run a simulated attack in the lab.
Example:
    Multiple failed SSH logins
        ↓
    Successful login
        ↓
    Suspicious command execution

### Minute 3–4: Detection
Dashboard updates:
    Risk: 85/100
    Incident: Possible account compromise
    Affected asset: linux-server-01
    Source IP: 192.168.1.55

### Minute 4–5: Explanation and Response
Show explanation:
Why suspicious?
    - 15 failed logins in 3 minutes.
    - Successful login after failed attempts.
    - Source IP not previously observed.
    - Login occurred outside business hours.

Show recommended action:
    Recommended action:
    - Reset user credentials.
    - Block source IP.
    - Review affected host.

### Demo Success Criteria
The demo is successful if:
    Wazuh alert is received,
    normalized event is stored,
    alert or incident is created,
    dashboard displays the result,
    explanation is understandable.
    
```text

