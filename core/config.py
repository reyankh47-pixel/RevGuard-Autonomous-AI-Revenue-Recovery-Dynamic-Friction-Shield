import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'revguard.db'

APP_NAME = 'RevGuard | AI Revenue Recovery & Risk Shield'
APP_VERSION = '2.0.0'
APP_DESCRIPTION = 'Autonomous AI Agent for Failed Payment Recovery and Dynamic Friction Risk Prevention'

SAFE_RISK_THRESHOLD = 40       # Score < 40: Safe (Zero friction)
SUSPICIOUS_RISK_THRESHOLD = 80 # Score 40-79: Dynamic Friction (OTP / Selfie)
                               # Score >= 80: High Risk / Fraud Blocked

DEFAULT_RECOVERY_DISCOUNT_PERCENT = 5.0
RECOVERY_EXPIRY_MINUTES = 60
SIMULATED_RAZORPAY_KEY = 'rzp_test_revguard_ai_2026'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
