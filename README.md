# RevGuard | AI Revenue Recovery & Dynamic Friction Agent

> Built for the **Razorpay Buildathon: AI Revenue Recovery**

## 🌟 Overview
**RevGuard** is an intelligent revenue protection and recovery platform that stops fraud without harming legitimate checkout conversions. By unifying **Phase 1 e-KYC Baseline Enrollment**, **Phase 2 Context-Aware Dynamic Friction**, and **Phase 3 Autonomous AI Revenue Recovery**, RevGuard saves merchants from lost cart revenue and payment failure drops.

---

## 🚀 Key Features

### 1. Phase 1: One-Time Secure Onboarding (e-KYC)
- Captures GPS telemetry, IP network signatures, and canvas device fingerprints.
- Vision AI agent simulates document OCR extraction & biometric liveness hashing.
- Enrolls verified user profile with a baseline risk score (0-100).

### 2. Phase 2: Context-Aware Dynamic Step-Up Friction
- Real-time telemetry comparison against user registration baseline.
- **Explainable AI Engine**: Generates auditable rationale bullets for every decision.
- **Dynamic Decision Routing**:
  - **Score < 40 (Safe)**: 1-Click Zero Friction Checkout.
  - **Score 40 - 79 (Suspicious)**: Dynamic Step-Up Challenge (OTP / Biometric Selfie).
  - **Score >= 80 (High Risk/Fraud)**: Instant Transaction Freeze & Shield.

### 3. Phase 3: Autonomous AI Revenue Recovery Workflows
- Triggers instantly on bank gateway timeouts (504), network drops, or hesitation drop-offs.
- AI Agent diagnoses root cause and calculates recovery probability.
- Executes omni-channel recovery:
  - Generates secure **1-Click Razorpay UPI Fallback Payment Links**.
  - Dynamic AI recovery incentives (e.g. 5% limited-time discount).
  - Dispatches personalized **WhatsApp / SMS / Email** recovery messages.
  - Integrated **AI Recovery Copilot Chat Assistant** for real-time customer support.

### 4. Merchant Command Center & Edge-Case Test Lab
- Live At-Risk vs. Recovered Revenue metrics & ROI counter.
- Real-time Explainable AI event stream.
- 1-Click presentation sandbox to demonstrate all scenarios live.

---

## 🛠️ How to Run

### Quick Start (Windows / PowerShell):
```powershell
cd razorpay-revguard
pip install -r requirements.txt
python main.py
```

Open your browser at: `http://localhost:8000`

### Pages:
- **Demo Store**: `http://localhost:8000/`
- **e-KYC Baseline Onboarding**: `http://localhost:8000/onboarding`
- **Merchant Command Center**: `http://localhost:8000/dashboard`
- **Hackathon Test Lab**: `http://localhost:8000/simulator`
