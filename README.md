🛡️ RevGuard: Autonomous AI Revenue Recovery & Risk Shield

[![Live Demo](https://img.shields.io/badge/Vercel-Live_Demo-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://rev-guard-autonomous-ai-revenue-rec.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/reyankh47-pixel/RevGuard-Autonomous-AI-Revenue-Recovery-Dynamic-Friction-Shield)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Razorpay Buildathon](https://img.shields.io/badge/Razorpay-Buildathon_2026-0C2340?style=for-the-badge&logo=razorpay&logoColor=white)](https://razorpay.com/)

> **Built for the Razorpay Buildathon: AI Revenue Recovery**  
> *An intelligent autonomous agent that eliminates checkout drop-offs, recovers failed payments in real-time, and shields merchants with dynamic context-aware security.*

---

## 🌐 Live Application Links

| Destination | Live URL | Purpose |
| :--- | :--- | :--- |
| 🛒 **Live Demo Store** | [https://rev-guard-autonomous-ai-revenue-rec.vercel.app/](https://rev-guard-autonomous-ai-revenue-rec.vercel.app/) | Interactive storefront with real-time risk assessment and dynamic checkout. |
| 🆔 **e-KYC Baseline Enrollment** | [https://rev-guard-autonomous-ai-revenue-rec.vercel.app/onboarding](https://rev-guard-autonomous-ai-revenue-rec.vercel.app/onboarding) | Phase 1 user identity registration with live GPS and device fingerprinting. |
| 📊 **Merchant Command Center** | [https://rev-guard-autonomous-ai-revenue-rec.vercel.app/dashboard](https://rev-guard-autonomous-ai-revenue-rec.vercel.app/dashboard) | Live recovered revenue analytics, recovery rates, and Explainable AI stream. |
| 🧪 **Presentation Test Lab** | [https://rev-guard-autonomous-ai-revenue-rec.vercel.app/simulator](https://rev-guard-autonomous-ai-revenue-rec.vercel.app/simulator) | 1-Click sandbox to demonstrate all edge cases live to hackathon judges. |

---

🎯 The Problem

Every year, digital merchants lose up to **30% of potential revenue** to two major flaws in payment flows:
1. **Dead-End Payment Failures**: Card network 504 timeouts, bank server downtime, or card limits display a dead-end *"Payment Failed"* screen. The customer leaves, and that sale is permanently lost.
2. **Checkout Friction & False Positives**: Static fraud detection forces legitimate shoppers through tedious OTP delays, driving cart abandonment. Blanket fraud rules reject good transactions.

---

## 💡 The Solution: RevGuard

**RevGuard bridges the gap between zero-friction conversion and autonomous revenue recovery** through a three-phase intelligent payment lifecycle.

### 🔐 Phase 1 — One-Time Secure Onboarding

RevGuard first establishes a trusted **e-KYC baseline** for the customer.

* 📍 Captures a **GPS location signal**
* 💻 Generates a **device/canvas fingerprint**
* 🔐 Creates a **SHA-256 hashed biometric identifier**
* 🧠 Builds a baseline profile for future transaction risk evaluation

**Goal:** Establish a trusted identity and device baseline before transactions begin.

⬇️

### ⚡ Phase 2 — Real-Time Context-Aware Dynamic Friction

During checkout, the **LLM-powered Risk Agent** compares live transaction telemetry against the customer's baseline profile and dynamically determines the appropriate security level.

| Risk Score | Decision       | Customer Experience                                    |
| :--------: | :------------- | :----------------------------------------------------- |
|  **< 40**  | 🟢 Low Risk    | **Zero-Friction 1-Click Checkout**                     |
|  **40–79** | 🟡 Medium Risk | **Dynamic Step-Up Challenge** — OTP / Biometric Selfie |
|  **≥ 80**  | 🔴 High Risk   | **Transaction Frozen & Shielded**                      |

Instead of applying the same authentication process to every customer, RevGuard introduces **friction only when the context demands it.**

⬇️

### 💰 Phase 3 — Autonomous AI Revenue Recovery Engine

If a payment fails or the customer drops off, RevGuard doesn't simply display a **"Payment Failed"** screen.

The **Revenue Recovery Engine** takes autonomous action:

**1. Diagnose the Failure**
Identifies the probable root cause, such as a bank outage, OTP hesitation, card limit, or other recoverable failure.

**2. Generate a Payment Fallback**
Creates a **one-click Razorpay UPI fallback payment link** to provide an alternative route to successful payment.

**3. Protect the Conversion Opportunity**
Offers a dynamic **5% recovery concession** where applicable and reserves cart inventory for **15 minutes**.

**4. Re-engage the Customer**
Dispatches personalized recovery notifications through **WhatsApp, SMS, or Email**.

**5. Complete the Recovery Journey**
Provides a live **AI Recovery Copilot** on the recovery checkout page to guide the customer toward successful payment.

---

### 🔄 The RevGuard Decision Loop

```text
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: SECURE ONBOARDING                                  │
│                                                             │
│ GPS Signal → Device Fingerprint → SHA-256 Biometric Hash   │
│                         ↓                                   │
│                 Trusted Baseline Profile                    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: DYNAMIC RISK ASSESSMENT                            │
│                                                             │
│ Live Telemetry → LLM Risk Agent → Dynamic Risk Score        │
│                                                             │
│   < 40        → Zero-Friction Checkout                      │
│   40–79       → Step-Up Authentication                      │
│   ≥ 80        → Transaction Frozen & Shielded               │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
                 Payment Failure / Drop-Off
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: AUTONOMOUS REVENUE RECOVERY                        │
│                                                             │
│ Diagnose → Fallback → Incentivize → Re-engage → Recover    │
│                                                             │
│ UPI Link + Recovery Concession + Cart Reservation           │
│ + WhatsApp/SMS/Email + AI Recovery Copilot                  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
                 💰 RECOVERED REVENUE
```

### 🎯 Core Philosophy

> **Don't add friction to every transaction. Don't abandon every failed payment.**
>
> **RevGuard dynamically decides when to trust, when to verify, and when to recover.**




---
## 🚀 Key Features
* **Real-time Geodesic Telemetry**: Calculates haversine distance between baseline coordinates and checkout GPS to catch spoofing.
* **Canvas Hardware Fingerprinting**: Identifies device signatures without invasive tracking.
* **Explainable AI (XAI) Audit Logs**: Generates human-readable decision logs explaining why transactions were approved or challenged.
* **Autonomous Omnichannel Recovery**: Multi-channel nudge generator formatting rich messages for WhatsApp, SMS, and Email.
* **Interactive AI Copilot**: Real-time customer support chatbot on recovery payment pages answering questions about failure causes, security, and discounts.
* **Merchant Analytics Hub**: Real-time KPI counter tracking At-Risk Revenue, AI-Recovered Revenue, and ROI.
---
## 🛠️ Tech Stack & Architecture
* **Backend**: Python 3.11+, FastAPI (high-concurrency ASGI)
* **Frontend**: HTML5, Tailwind CSS, Modern Glassmorphism, Vanilla JavaScript
* **Database**: SQLite (with automatic serverless `/tmp` compatibility for Vercel)
* **Templating**: Jinja2
* **Deployment**: Vercel Serverless Functions + GitHub Actions
---
## 💻 Local Quick Start
### 1. Clone the Repository
```bash
git clone https://github.com/reyankh47-pixel/RevGuard-Autonomous-AI-Revenue-Recovery-Dynamic-Friction-Shield.git
cd RevGuard-Autonomous-AI-Revenue-Recovery-Dynamic-Friction-Shield
2. Install Dependencies
bash


pip install -r requirements.txt
3. Start the Server
bash


python main.py
Open http://localhost:8000 in your browser.

(On Windows, you can also simply double-click run.bat).

📜 License & Acknowledgements
Built with ❤️ for the Razorpay Buildathon: AI Revenue Recovery.



</details>
4. Click **"Commit changes"**.
---
#### 2. Update `PROJECT_GUIDE.md` on GitHub
1. Click on **`PROJECT_GUIDE.md`** on GitHub ➔ Click the **Pencil icon ✏️**.
2. Replace with the updated guide content from [`PROJECT_GUIDE.md`](file:///C:/Users/user/.gemini/antigravity/scratch/razorpay-revguard/PROJECT_GUIDE.md).
3. Click **"Commit changes"**.


**RevGuard** bridges the gap between **zero-friction conversion** and **automated revenue recovery**:
