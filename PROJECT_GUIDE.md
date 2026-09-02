# RevGuard: Autonomous AI Revenue Recovery & Risk Shield
## Complete Project Guide, Architecture Breakdown & Hackathon Presentation Script

---

## 🎯 1. Project Motive & Core Problem

### The Problem in Modern Digital Payments
Every year, e-commerce platforms and merchants lose **billions in revenue** due to two conflicting problems:

1. **Payment Failures & Cart Abandonment (Lost Revenue)**:
   - **Bank Gateway Outages / Latency**: The customer’s bank server is temporarily down (504 gateway timeout), card limits are hit, or networks drop.
   - **Friction Drop-offs**: Unnecessary OTP screens, slow SMS delivery, and tedious verification cause frustrated buyers to abandon their carts.
   - **No Automated Recovery**: Most payment gateways simply show *"Payment Failed - Try Again"*, leaving the merchant with zero automated workflow to recapture the lost sale.

2. **The Fraud vs. Conversion Dilemma (False Positives)**:
   - Traditional fraud prevention rules are **static and rigid** (e.g., blanket blocking any transaction from a new IP or requiring heavy OTP friction on every single purchase).
   - High friction drives away legitimate customers (lost conversion).
   - Low friction allows real fraudsters and bots to execute stolen card attacks.

---

### The Solution: RevGuard
**RevGuard** bridges the gap between **Fraud Prevention** and **Autonomous Revenue Recovery**:
- **For Legitimate Buyers**: It offers **Zero Friction 1-Click Checkout** by comparing live context signals against an initial e-KYC baseline.
- **For Suspicious Activity**: It introduces **Dynamic Step-Up Friction** (OTP or Biometric Selfie challenge) only when risk is detected.
- **When Payments Fail or Drop Off**: Instead of losing the sale, RevGuard's **Autonomous AI Recovery Agent** immediately diagnoses the root cause, provisions a **1-Click Fallback Razorpay UPI Payment Link**, offers dynamic incentives, sends multi-channel nudges (WhatsApp / SMS / Email), and provides an interactive **AI Recovery Copilot Chat Assistant** to recover the revenue in real-time.

---

## 🏗️ 2. High-Level Architecture (The 3 Phases)

```
+---------------------------------------------------------------------------------------+
| PHASE 1: ONE-TIME SECURE ONBOARDING (e-KYC Baseline)                                  |
| 1. User registers -> 2. GPS Ping & Canvas Fingerprint -> 3. Upload Gov ID             |
| 4. Vision AI Agent (OCR & Biometric Face Hash) -> 5. Enrolls Baseline Profile in DB   |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| PHASE 2: REAL-TIME SECURE CHECKOUT (Dynamic Friction)                                 |
| 1. Live Telemetry Capture (Live GPS, IP/Network, Canvas Hardware Fingerprint)         |
| 2. LLM Risk Agent compares signals with Baseline Profile                              |
| 3. Computes Risk Score (0-100) + Generates Explainable AI Log                         |
|                                                                                       |
|   * Score < 40 (Safe):         Payment Approved (Zero Friction 1-Click)               |
|   * Score 40-79 (Suspicious):  Dynamic Friction (Step-Up OTP / Selfie Challenge)      |
|   * Score >= 80 (Fraud):       Transaction Frozen & Shielded                          |
+---------------------------------------------------------------------------------------+
                                           | (On Failure or Drop-Off)
                                           v
+---------------------------------------------------------------------------------------+
| PHASE 3: AUTONOMOUS AI REVENUE RECOVERY ENGINE                                        |
| 1. Root-Cause Diagnostic (Bank Downtime vs. OTP Drop-Off vs. Card Limit)              |
| 2. Strategy Computation (Instant UPI Fallback / 15-Min Stock Lock / Dynamic 5% Off)   |
| 3. Multi-Channel Dispatch (WhatsApp / SMS / Email Nudges)                             |
| 4. Dedicated 1-Click Razorpay UPI Recovery Portal (/recover/{token})                  |
| 5. Live AI Recovery Copilot Chat Assistant                                            |
| 6. Payment Recovered -> Metric Logged to Merchant Command Center                      |
+---------------------------------------------------------------------------------------+
```

---

## ⚙️ 3. How Each Component Works (Under the Hood)

### A. Device Telemetry Harvester (`core/telemetry.py`)
- **Canvas Fingerprint**: Generates a deterministic hardware signature by drawing hidden 2D/WebGL canvas patterns and computing a cryptographic hash.
- **Geodesic Haversine Distance**: Uses the spherical trigonometry formula to calculate the exact physical distance between the user's registered baseline coordinates and their current transaction GPS ping.
- **Network Anomaly Detector**: Identifies VPNs, data center proxy subnets, and Tor exit nodes.

### B. Vision AI & e-KYC Agent (`agents/kyc_agent.py`)
- Simulates official ID parsing (Aadhaar, Driving License, Passport, PAN).
- Creates an immutable SHA-256 biometric face hash representing user identity.
- Sets an initial trusted baseline risk score ($5 - 12 / 100$).

### C. LLM Risk Agent & Explainable AI (`agents/risk_agent.py`)
- Evaluates 5 dimensions:
  1. *Geo-Drift Distance*: ($0\text{km}$ = Safe, $>350\text{km}$ = $+35$ risk).
  2. *Device Match*: (Baseline match = $0$, unknown hardware signature = $+25$ risk).
  3. *Network Integrity*: (Residential ISP = $0$, VPN/Tor/Proxy = $+35$ risk).
  4. *Transaction Velocity & Amount*: ($>3\times$ average order limit = $+15$ risk).
  5. *KYC Status*: (Verified profile = $-10$ bonus trust).
- Produces human-readable **Explainable AI audit logs** so merchants understand the exact reasoning behind every decision.

### D. Autonomous Revenue Recovery Engine (`agents/recovery_agent.py`)
- **Failure Classification Matrix**:
  | Failure Trigger | Root Cause | AI Recovery Strategy | Channel & Action |
  | :--- | :--- | :--- | :--- |
  | **`BANK_DOWNTIME`** | Card gateway/issuer timeout (504) | Instant UPI Fallback | Bypasses card rails; provisions 1-click Razorpay UPI link via WhatsApp. |
  | **`OTP_TIMEOUT` / `FRICTION_DROPOUT`** | Customer hesitated at verification step | Stock Lock & Frictionless Link | Reserves cart inventory for 15 minutes; sends 1-click resume link. |
  | **`CARD_LIMIT_DECLINE`** | Daily card limit reached | Alternate Rail / Split Pay | Offers zero-surcharge UPI or Split payments. |
  | **`ABANDONED_CHECKOUT`** | Hesitant shopper paused | Dynamic AI Concession | Unlocks a dynamic 5% recovery discount coupon (`REVRECOVER5`). |
- **AI Recovery Copilot Chatbot**: An embedded intelligent assistant on the customer's recovery payment page that answers questions about payment safety, explains failure reasons, confirms discount savings, and guides the customer to completion.

---

## 🎤 4. Pitch & Presentation Guide for the Hackathon Judges

When presenting to judges or reviewers, use this **3-minute pitch outline**:

### 1. The Hook (30 Seconds)
> *"Every year, e-commerce stores lose up to 30% of their revenue to failed transactions, bank server timeouts, and friction drop-offs. At the same time, merchants lose sales due to false-positive fraud blocks. We built **RevGuard**—an AI Revenue Recovery and Risk Shield that eliminates friction for verified buyers, applies dynamic security when needed, and autonomously recovers lost revenue when payments fail."*

### 2. The 3-Phase Architecture Walkthrough (60 Seconds)
1. **Show Phase 1 (`/onboarding`)**:
   > *"First, the customer completes a one-time onboarding. We capture their device canvas fingerprint, GPS baseline, and generate a verified biometric hash."*
2. **Show Phase 2 (`/`)**:
   > *"During checkout, our LLM Risk Agent compares live context against the baseline. If the user is at home on their registered device, risk is under 40—they get instant zero-friction payment. If we detect an anomaly (e.g., a 1,700km geo-drift), the system dynamically challenges them with an OTP or selfie."*
3. **Show Phase 3 (`/recover/{token}` & `/dashboard`)**:
   > *"If an issuer bank goes down or a user abandons during step-up, our Autonomous AI Recovery Agent instantly triggers. It diagnoses the root cause, reserves the cart, applies a dynamic recovery incentive, and dispatches a 1-click Razorpay UPI fallback link with an embedded AI Copilot assistant."*

### 3. Live 1-Click Sandbox Demo (`/simulator`) (60 Seconds)
Open `/simulator` and run:
- **Scenario A**: Verified Safe User $\rightarrow$ Instant Approval.
- **Scenario B**: Geo-Drift $\rightarrow$ Dynamic Step-Up Challenge.
- **Scenario C**: Bank Outage $\rightarrow$ Autonomous AI UPI Recovery Link generation.
- **Scenario D**: Step-Up Abandonment $\rightarrow$ WhatsApp 1-Click Recovery Nudge.
- **Scenario E**: Tor Bot Attack $\rightarrow$ High-Risk Fraud Freeze.

### 4. The Business Impact & ROI (30 Seconds)
Open `/dashboard`:
> *"On the Merchant Hub, store owners have full visibility into Total At-Risk Revenue, AI Recovered Revenue, Recovery Conversion Rate %, and live Explainable AI audit logs. RevGuard turns failed payments into completed revenue automatically."*

---

## 💻 5. Quick Reference: Application Routes

| Web Page / Endpoint | URL | Purpose |
| :--- | :--- | :--- |
| **Demo E-Commerce Store** | `http://localhost:8000/` | Interactive shopping catalog, persona switcher, telemetry simulation, and dynamic checkout. |
| **e-KYC Baseline Portal** | `http://localhost:8000/onboarding` | Phase 1 identity onboarding, GPS ping, and biometric hash creation. |
| **Merchant Command Center** | `http://localhost:8000/dashboard` | Executive revenue metrics, active recovery pipeline, and live Explainable AI stream. |
| **Presentation Test Lab** | `http://localhost:8000/simulator` | 1-Click edge-case sandbox to demonstrate all scenarios to judges. |
| **Customer Recovery Portal** | `http://localhost:8000/recover/{token}` | Customer 1-click fallback payment page with AI Copilot chat. |

---

## 🛠️ 6. How to Run Anytime
```powershell
cd C:\Users\user\.gemini\antigravity\scratch\razorpay-revguard
python main.py
```
Open **`http://localhost:8000`** in your browser.
