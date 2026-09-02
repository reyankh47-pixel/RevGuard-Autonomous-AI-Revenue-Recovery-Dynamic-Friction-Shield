import json
import uuid
import random
from datetime import datetime, timedelta
try:
    from ..core.database import get_db
    from ..core.config import DEFAULT_RECOVERY_DISCOUNT_PERCENT, RECOVERY_EXPIRY_MINUTES
except ImportError:
    from core.database import get_db
    from core.config import DEFAULT_RECOVERY_DISCOUNT_PERCENT, RECOVERY_EXPIRY_MINUTES

class RecoveryAgent:
    """
    Autonomous AI Revenue Recovery Engine
    Detects at-risk revenue (failed payments, abandoned checkouts, friction drop-outs)
    and executes multi-channel automated workflows to recover the sale.
    """

    @staticmethod
    def trigger_recovery(
        order_id: str,
        failure_reason: str,
        failure_detail: str = "",
        user_id: str = None
    ) -> dict:
        conn = get_db()
        cursor = conn.cursor()

        # Fetch transaction details
        cursor.execute("SELECT * FROM transactions WHERE order_id = ?", (order_id,))
        tx_row = cursor.fetchone()

        if not tx_row:
            # Create a provisional transaction if not already existing
            cursor.execute("""
                INSERT INTO transactions (order_id, user_id, amount, status, failure_reason, failure_detail)
                VALUES (?, ?, ?, 'FAILED', ?, ?)
            """, (order_id, user_id or "USR-78291", 4999.0, failure_reason, failure_detail))
            conn.commit()
            cursor.execute("SELECT * FROM transactions WHERE order_id = ?", (order_id,))
            tx_row = cursor.fetchone()

        tx = dict(tx_row)
        user_id = user_id or tx.get("user_id", "USR-78291")
        original_amount = tx.get("amount", 4999.0)

        # Fetch user info
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()
        user = dict(user_row) if user_row else {
            "name": "Valued Customer",
            "phone": "+91 98765 43210",
            "email": "customer@example.com"
        }

        # Generate unique recovery token
        recovery_token = f"rcv_{uuid.uuid4().hex[:12]}"
        
        # Diagnostic & Recovery Strategy Engine
        discount_percent = 0.0
        if failure_reason in ["BANK_DOWNTIME", "ISSUER_TIMEOUT", "GATEWAY_ERROR"]:
            strategy_type = "INSTANT_UPI_FALLBACK"
            channel_dispatched = "WHATSAPP"
            recovery_probability = 88.5
            ai_rationale = (
                "Bank card issuer gateway experienced temporary latency. "
                "AI Agent generated instant 1-click Razorpay UPI intent link to bypass failed banking rail without re-entering card details."
            )
            discount_percent = 0.0
        elif failure_reason in ["OTP_TIMEOUT", "FRICTION_DROPOUT", "STEP_UP_ABANDONED"]:
            strategy_type = "STEP_UP_RESUME_WITH_RESERVATION"
            channel_dispatched = "WHATSAPP"
            recovery_probability = 76.0
            ai_rationale = (
                "Customer dropped off during dynamic verification step. "
                "AI Agent sent a personalized WhatsApp nudge reserving cart stock for 15 minutes with 1-click biometric re-authentication."
            )
            discount_percent = DEFAULT_RECOVERY_DISCOUNT_PERCENT
        elif failure_reason in ["INSUFFICIENT_FUNDS", "CARD_LIMIT_DECLINE"]:
            strategy_type = "SPLIT_PAY_OR_UPI_ALTERNATIVE"
            channel_dispatched = "SMS"
            recovery_probability = 68.0
            ai_rationale = (
                "Card transaction declined due to daily card limit. "
                "AI Agent offered instant alternate UPI payment or split EMI options with zero processing surcharge."
            )
            discount_percent = DEFAULT_RECOVERY_DISCOUNT_PERCENT
        else: # ABANDONED_CHECKOUT or general failure
            strategy_type = "DYNAMIC_INCENTIVE_RECOVERY"
            channel_dispatched = "EMAIL"
            recovery_probability = 82.0
            discount_percent = DEFAULT_RECOVERY_DISCOUNT_PERCENT
            ai_rationale = (
                f"Checkout paused prior to final confirmation. "
                f"AI Agent unlocked a time-sensitive {DEFAULT_RECOVERY_DISCOUNT_PERCENT}% recovery concession to maximize purchase completion."
            )

        recovery_amount = round(original_amount * (1.0 - (discount_percent / 100.0)), 2)

        # Dynamic Omnichannel Messages
        recovery_url = f"/recover/{recovery_token}"

        whatsapp_msg = (
            f"👋 Hi {user.get('name', 'there')}, we noticed your recent order #{order_id} (₹{original_amount:,.2f}) couldn't be completed due to {failure_reason.replace('_', ' ').title()}.\n\n"
            f"✨ Good news: RevGuard AI has safely preserved your items. "
            + (f"We've applied an exclusive {discount_percent}% savings for you! Final Amount: ₹{recovery_amount:,.2f}.\n\n" if discount_percent > 0 else f"Amount: ₹{recovery_amount:,.2f}.\n\n")
            + f"👉 Tap here to complete your payment securely in 1-click: {recovery_url}"
        )

        sms_msg = (
            f"RevGuard Alert: Your order #{order_id} is reserved. Complete 1-click payment now (₹{recovery_amount:,.2f}): {recovery_url}"
        )

        email_msg = (
            f"Subject: Secure 1-Click Recovery for Order #{order_id}\n\n"
            f"Hello {user.get('name')},\n"
            f"Your order of ₹{original_amount:,.2f} encountered a temporary payment gateway issue ({failure_reason}).\n"
            f"Our automated recovery agent has provisioned a dedicated fallback checkout session.\n"
            f"New Total: ₹{recovery_amount:,.2f}\n\n"
            f"Click here to finish checkout: {recovery_url}"
        )

        message_payload = {
            "whatsapp": whatsapp_msg,
            "sms": sms_msg,
            "email": email_msg
        }

        # Update transaction status to FAILED or ABANDONED
        cursor.execute("""
            UPDATE transactions
            SET status = 'AT_RISK_RECOVERY_IN_PROGRESS',
                failure_reason = ?,
                failure_detail = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
        """, (failure_reason, failure_detail, order_id))

        # Insert recovery workflow
        cursor.execute("""
            INSERT INTO recovery_workflows (
                transaction_id, order_id, user_id, recovery_token,
                strategy_type, original_amount, recovery_amount,
                discount_percent, channel_dispatched, message_content,
                ai_rationale, recovery_probability, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'TRIGGERED')
        """, (
            tx.get("id", 1), order_id, user_id, recovery_token,
            strategy_type, original_amount, recovery_amount,
            discount_percent, channel_dispatched, json.dumps(message_payload),
            ai_rationale, recovery_probability
        ))

        # Log to telemetry events stream
        cursor.execute("""
            INSERT INTO telemetry_events (
                event_type, user_id, order_id, risk_score, action_taken, details_json
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "AI_RECOVERY_WORKFLOW_DISPATCHED",
            user_id,
            order_id,
            tx.get("risk_score", 0.0),
            strategy_type,
            json.dumps({
                "strategy": strategy_type,
                "channel": channel_dispatched,
                "original_amount": original_amount,
                "recovery_amount": recovery_amount,
                "discount_percent": discount_percent,
                "probability": f"{recovery_probability}%",
                "recovery_url": recovery_url,
                "ai_rationale": ai_rationale
            })
        ))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "order_id": order_id,
            "user_id": user_id,
            "recovery_token": recovery_token,
            "recovery_url": recovery_url,
            "strategy_type": strategy_type,
            "channel_dispatched": channel_dispatched,
            "original_amount": original_amount,
            "recovery_amount": recovery_amount,
            "discount_percent": discount_percent,
            "recovery_probability": recovery_probability,
            "ai_rationale": ai_rationale,
            "messages": message_payload
        }

    @staticmethod
    def complete_recovery(recovery_token: str, payment_method: str = "Razorpay UPI 1-Click") -> dict:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM recovery_workflows WHERE recovery_token = ?", (recovery_token,))
        wf_row = cursor.fetchone()

        if not wf_row:
            conn.close()
            return {"success": False, "message": "Recovery token not found or expired."}

        wf = dict(wf_row)
        order_id = wf.get("order_id")
        recovered_amount = wf.get("recovery_amount")
        user_id = wf.get("user_id")

        # Mark workflow completed
        cursor.execute("""
            UPDATE recovery_workflows
            SET status = 'COMPLETED',
                completed_at = CURRENT_TIMESTAMP
            WHERE recovery_token = ?
        """, (recovery_token,))

        # Update transaction status
        cursor.execute("""
            UPDATE transactions
            SET status = 'RECOVERED',
                payment_method = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
        """, (payment_method, order_id))

        # Log event
        cursor.execute("""
            INSERT INTO telemetry_events (
                event_type, user_id, order_id, action_taken, details_json
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            "REVENUE_RECOVERED_SUCCESS",
            user_id,
            order_id,
            "PAYMENT_RECOVERED",
            json.dumps({
                "recovered_amount": recovered_amount,
                "strategy_type": wf.get("strategy_type"),
                "payment_method": payment_method,
                "recovery_token": recovery_token
            })
        ))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "order_id": order_id,
            "recovered_amount": recovered_amount,
            "payment_method": payment_method,
            "message": f"Successfully recovered ₹{recovered_amount:,.2f} for Order #{order_id} via {payment_method}!"
        }

    @staticmethod
    def answer_copilot_query(question: str, recovery_context: dict) -> str:
        """
        AI Recovery Copilot Chat Assistant for customers on the recovery payment page.
        """
        q = question.lower()
        amount = recovery_context.get("recovery_amount", 4999.0)
        orig = recovery_context.get("original_amount", 4999.0)
        strategy = recovery_context.get("strategy_type", "UPI")

        if "why" in q and ("fail" in q or "failed" in q or "decline" in q):
            return (
                f"Your earlier transaction failed due to temporary issuer network timeout or verification drop-off. "
                f"RevGuard AI has re-routed the transaction through our high-availability 1-click payment rail so you can finish safely without card re-entry."
            )
        elif "discount" in q or "coupon" in q or "save" in q or "price" in q:
            if orig > amount:
                return (
                    f"Yes! An automated {recovery_context.get('discount_percent', 5)}% RevGuard recovery incentive has already been applied. "
                    f"Your original total was ₹{orig:,.2f}, and your special recovered price is now ₹{amount:,.2f}."
                )
            else:
                return f"Your cart is preserved at ₹{amount:,.2f} with zero processing fees."
        elif "safe" in q or "secure" in q or "fraud" in q or "protect" in q:
            return (
                "Your checkout session is protected with end-to-end 256-bit encryption, biometric device hashing, "
                "and Razorpay PCI-DSS Level 1 compliant secure tokenization."
            )
        elif "upi" in q or "google pay" in q or "phonepe" in q or "paytm" in q:
            return "Yes! You can complete this instantly with any UPI app (Google Pay, PhonePe, Paytm, CRED, or BHIM) using the 1-click button or QR code below."
        else:
            return (
                f"I'm here to assist you with completing your order for ₹{amount:,.2f}. "
                f"You can pay seamlessly via UPI QR, 1-Click Intent, or NetBanking. Would you like me to guide you through payment?"
            )
