import json
import random
from datetime import datetime
try:
    from ..core.database import get_db
    from ..core.telemetry import analyze_telemetry_signals
    from ..core.config import SAFE_RISK_THRESHOLD, SUSPICIOUS_RISK_THRESHOLD
except ImportError:
    from core.database import get_db
    from core.telemetry import analyze_telemetry_signals
    from core.config import SAFE_RISK_THRESHOLD, SUSPICIOUS_RISK_THRESHOLD

class RiskAgent:
    """
    LLM Risk Agent & Real-time Dynamic Friction Engine
    Compares live transaction telemetry with user baseline and generates Explainable AI logs.
    """

    @staticmethod
    def evaluate_transaction(
        user_id: str,
        order_id: str,
        amount: float,
        payment_method: str,
        live_telemetry: dict
    ) -> dict:
        conn = get_db()
        cursor = conn.cursor()

        # Fetch historical user baseline
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()

        if user_row:
            user_data = dict(user_row)
            base_risk = user_data.get("risk_baseline", 10.0)
            baseline = {
                "gps_lat": user_data.get("gps_lat", 12.9716),
                "gps_lng": user_data.get("gps_lng", 77.5946),
                "gps_city": user_data.get("gps_city", "Bengaluru, India"),
                "ip_address": user_data.get("ip_address", "103.21.124.55"),
                "device_hash": user_data.get("device_hash", ""),
                "kyc_status": user_data.get("kyc_status", "VERIFIED")
            }
        else:
            # Guest or unknown profile
            base_risk = 35.0
            baseline = {
                "gps_lat": 12.9716,
                "gps_lng": 77.5946,
                "gps_city": "Unknown",
                "ip_address": "Unknown",
                "device_hash": "unregistered_device",
                "kyc_status": "UNVERIFIED"
            }

        # Analyze telemetry against baseline
        analysis = analyze_telemetry_signals(baseline, live_telemetry)

        # Compute Total Risk Score
        total_risk = base_risk + analysis["risk_points"]

        # Transaction value anomaly check
        if amount > 15000.0:
            total_risk += 15.0
            analysis["reasons"].append(f"High-Value Order: ₹{amount:,.2f} exceeds standard 1-click single-session limits.")
        else:
            analysis["reasons"].append(f"Transaction Value: ₹{amount:,.2f} is within normal authorized spending tier.")

        # Cap between 0 and 100
        risk_score = round(min(max(total_risk, 0.0), 100.0), 1)

        # Decision Routing
        if risk_score < SAFE_RISK_THRESHOLD:
            decision = "APPROVED_SAFE"
            action_label = "Payment Approved (Zero Friction)"
            friction_type = "NONE"
            explanation_summary = "Risk score is below safe threshold. Identity, location, and device fingerprints fully verified against historical baseline."
        elif risk_score < SUSPICIOUS_RISK_THRESHOLD:
            decision = "DYNAMIC_FRICTION_REQUIRED"
            action_label = "Dynamic Friction Required (Step-Up Challenge)"
            friction_type = "OTP_OR_SELFIE"
            explanation_summary = "Moderate risk signals detected. Automated step-up challenge triggered to authenticate account holder and prevent unauthorized charge."
        else:
            decision = "BLOCKED_FRAUD"
            action_label = "Transaction Blocked (High Risk / Fraud Prevented)"
            friction_type = "BLOCK"
            explanation_summary = "High risk velocity and critical telemetry mismatch. Immediate transaction freeze to protect merchant revenue and account security."

        # Compile Explainable AI Log
        explainable_log = {
            "risk_score": risk_score,
            "decision": decision,
            "action_label": action_label,
            "friction_type": friction_type,
            "summary": explanation_summary,
            "baseline_city": baseline.get("gps_city"),
            "geo_distance_km": analysis.get("geo_distance_km", 0),
            "reasons": analysis.get("reasons", [])
        }

        # Save/Update transaction in database
        cursor.execute("""
            INSERT OR REPLACE INTO transactions (
                order_id, user_id, amount, status, risk_score,
                telemetry_json, explainable_ai_log, payment_method
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id, user_id, amount, decision, risk_score,
            json.dumps(live_telemetry), json.dumps(explainable_log), payment_method
        ))

        # Log Telemetry Event Stream
        cursor.execute("""
            INSERT INTO telemetry_events (
                event_type, user_id, order_id, risk_score, action_taken, details_json
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "TRANSACTION_RISK_EVALUATION",
            user_id,
            order_id,
            risk_score,
            decision,
            json.dumps(explainable_log)
        ))

        conn.commit()
        conn.close()

        return {
            "order_id": order_id,
            "user_id": user_id,
            "amount": amount,
            "risk_score": risk_score,
            "decision": decision,
            "action_label": action_label,
            "friction_type": friction_type,
            "explainable_log": explainable_log
        }
