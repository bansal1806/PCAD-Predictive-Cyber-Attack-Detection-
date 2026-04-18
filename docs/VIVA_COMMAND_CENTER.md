# PCAD Viva Command Center 🎖️

A technical "cheat sheet" for your presentation. Use these talking points to demonstrate deep expertise.

---

### 🧠 1. The Strategy: Prediction vs. Detection
*   **The "Why":** Most IDS (Intrusion Detection Systems) find attacks *after* they happen. PCAD focuses on **Prediction**.
*   **The Mechanism:** We aggregate raw network flows into **5-minute sliding windows**. We don't just look at one packet; we look at the *behavioral trend* of the last 5 minutes to predict the threat level of the *next* block.

### ⚙️ 2. The Innovation: Feature Engineering
*   **Rolling Features:** We use **EWMA (Exponential Weighted Moving Average)** and **Rolling Std Dev**. This captures "Burstiness" — a key indicator of DDoS or Port Scanning.
*   **Feature Count (37):** We reduced 79 raw features to 37 high-signal behavioral aggregates. This prevents "Overfitting" and makes the model faster for real-time edge deployment.

### 🤖 3. The Brain: Ensemble Learning
*   **The Choice:** We use a **Soft Voting Ensemble** (Random Forest + XGBoost + KNN).
*   **The Benefit:** XGBoost is great at finding outliers (Anomalies), while Random Forest is robust to noise. Together, they reduce "False Positives" which is the biggest pain point in cybersecurity.

### 🛡️ 4. The Shield: Multi-Layer Security
*   **Hardened API:** The system uses **API Key Authentication** (X-API-KEY) and **Rate Limiting** to prevent an attacker from spamming the "Prediction" engine to find bypasses.
*   **Audit Trail:** Every high-probability detection is written to `logs/security_audit.log`, ensuring a permanent record for forensics.

### 🔍 5. Explainable AI (XAI) with SHAP
*   **The "Black Box" Problem:** If an automated system blocks a CEO's laptop, YOU need to know why.
*   **The Solution:** **SHAP values** mathematically break down *which* specific feature (e.g., `Flow IAT Max` or `Fwd Packets/s`) pushed the model toward an "Attack" decision. It transforms ML into an "Actionable Insight" tool.

---

### ⚡ Troubleshooting / FAQ for Viva
*   **"What if a new attack comes out?"**
    > PCAD is trained on the CIC-IDS 2017 dataset, but its "Temporal Rolling Features" are designed to catch *behavioral patterns* (like high frequency or unusual destination counts) rather than specific fixed signatures.
*   **"Why 5-minute windows?"**
    > It's a balance. 1 minute is too noisy; 10 minutes is too slow for response. 5 minutes provides enough context for a stable prediction while remaining responsive.
