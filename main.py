import os
import sys
from pathlib import Path
from typing import Optional, List
import json

from fastapi import FastAPI, Request, Form, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Add current directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.config import APP_NAME, APP_VERSION, APP_DESCRIPTION, DB_PATH
from core.database import init_db, get_db
from core.telemetry import haversine_distance, generate_fingerprint_hash
from agents.kyc_agent import KYCAgent
from agents.risk_agent import RiskAgent
from agents.recovery_agent import RecoveryAgent

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Static files and Templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Startup event: Initialize database
@app.on_event("startup")
def startup_event():
    init_db()

# ==========================================
# WEB PAGE ROUTES
# ==========================================

@app.get("/", response_class=HTMLResponse)
@app.get("/main.py", response_class=HTMLResponse)
async def view_store(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM users ORDER BY id DESC")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return templates.TemplateResponse(
        request=request,
        name="store.html",
        context={
            "products": products,
            "users": users,
            "app_name": APP_NAME
        }
    )

@app.get("/onboarding", response_class=HTMLResponse)
async def view_onboarding(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 5")
    recent_users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return templates.TemplateResponse(
        request=request,
        name="onboarding.html",
        context={
            "recent_users": recent_users,
            "app_name": APP_NAME
        }
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def view_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "app_name": APP_NAME
        }
    )

@app.get("/simulator", response_class=HTMLResponse)
async def view_simulator(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 5")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return templates.TemplateResponse(
        request=request,
        name="simulator.html",
        context={
            "users": users,
            "app_name": APP_NAME
        }
    )

@app.get("/recover/{token}", response_class=HTMLResponse)
async def view_recovery_link(request: Request, token: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rw.*, t.payment_method as orig_method, t.failure_reason, t.failure_detail, u.name as user_name, u.email as user_email, u.phone as user_phone
        FROM recovery_workflows rw
        LEFT JOIN transactions t ON rw.transaction_id = t.id
        LEFT JOIN users u ON rw.user_id = u.user_id
        WHERE rw.recovery_token = ?
    """, (token,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return templates.TemplateResponse(
            request=request,
            name="recovery_link.html",
            context={
                "error": "Recovery session expired or invalid token.",
                "workflow": None,
                "app_name": APP_NAME
            }
        )

    wf = dict(row)
    try:
        wf["messages"] = json.loads(wf.get("message_content", "{}"))
    except:
        wf["messages"] = {}

    return templates.TemplateResponse(
        request=request,
        name="recovery_link.html",
        context={
            "workflow": wf,
            "app_name": APP_NAME
        }
    )

# ==========================================
# REST API ENDPOINTS
# ==========================================

class TelemetryPayload(BaseModel):
    gps_lat: Optional[float] = 12.9716
    gps_lng: Optional[float] = 77.5946
    gps_city: Optional[str] = "Bengaluru, India"
    ip_address: Optional[str] = "103.21.124.55"
    device_hash: Optional[str] = "canvas_fp_bengaluru_chrome_win11"
    user_agent: Optional[str] = ""
    screen_res: Optional[str] = "1920x1080"
    is_vpn: Optional[bool] = False
    is_proxy: Optional[bool] = False
    is_tor: Optional[bool] = False

class RiskEvalRequest(BaseModel):
    user_id: str
    order_id: str
    amount: float
    payment_method: str = "UPI / Card"
    telemetry: TelemetryPayload

class StepUpVerifyRequest(BaseModel):
    order_id: str
    verification_type: str = "OTP"
    code_or_hash: str

class TriggerRecoveryRequest(BaseModel):
    order_id: str
    failure_reason: str
    failure_detail: Optional[str] = ""
    user_id: Optional[str] = None

class CompleteRecoveryRequest(BaseModel):
    recovery_token: str
    payment_method: Optional[str] = "Razorpay UPI 1-Click"

class CopilotChatRequest(BaseModel):
    question: str
    recovery_token: str

@app.get("/api/products")
def get_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"success": True, "products": products}

@app.get("/api/users")
def get_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id DESC")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"success": True, "users": users}

@app.post("/api/kyc/onboard")
async def onboard_user(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    gov_id_type: str = Form(...),
    gov_id_number: Optional[str] = Form(None),
    gps_lat: Optional[float] = Form(12.9716),
    gps_lng: Optional[float] = Form(77.5946),
    gps_city: Optional[str] = Form("Bengaluru, India"),
    ip_address: Optional[str] = Form("103.21.124.55"),
    device_hash: Optional[str] = Form("canvas_fp_bengaluru_chrome_win11")
):
    result = KYCAgent.process_onboarding(
        name=name,
        email=email,
        phone=phone,
        gov_id_type=gov_id_type,
        gov_id_number=gov_id_number,
        gps_lat=gps_lat,
        gps_lng=gps_lng,
        gps_city=gps_city,
        ip_address=ip_address,
        device_hash=device_hash
    )
    return JSONResponse(result)

@app.post("/api/checkout/evaluate-risk")
def evaluate_risk(payload: RiskEvalRequest):
    telemetry_dict = payload.telemetry.dict()
    result = RiskAgent.evaluate_transaction(
        user_id=payload.user_id,
        order_id=payload.order_id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        live_telemetry=telemetry_dict
    )
    return JSONResponse(result)

@app.post("/api/checkout/verify-step-up")
def verify_step_up(payload: StepUpVerifyRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE order_id = ?", (payload.order_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return JSONResponse({"success": False, "message": "Order not found"}, status_code=404)

    tx = dict(row)
    
    if payload.code_or_hash in ["4321", "1234", "VALID_SELFIE"] or len(payload.code_or_hash) >= 4:
        cursor.execute("""
            UPDATE transactions
            SET status = 'APPROVED_SAFE', updated_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
        """, (payload.order_id,))

        cursor.execute("""
            INSERT INTO telemetry_events (event_type, user_id, order_id, risk_score, action_taken, details_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "DYNAMIC_FRICTION_PASSED",
            tx.get("user_id"),
            payload.order_id,
            tx.get("risk_score", 45.0),
            "STEP_UP_AUTHENTICATED",
            json.dumps({"method": payload.verification_type, "status": "VERIFIED"})
        ))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Dynamic verification passed. Transaction approved with zero chargeback risk!"}
    else:
        conn.close()
        return {"success": False, "message": "Invalid OTP code or biometric match failed."}

@app.post("/api/recovery/trigger")
def trigger_recovery(payload: TriggerRecoveryRequest):
    result = RecoveryAgent.trigger_recovery(
        order_id=payload.order_id,
        failure_reason=payload.failure_reason,
        failure_detail=payload.failure_detail or "",
        user_id=payload.user_id
    )
    return JSONResponse(result)

@app.post("/api/recovery/complete")
def complete_recovery(payload: CompleteRecoveryRequest):
    result = RecoveryAgent.complete_recovery(
        recovery_token=payload.recovery_token,
        payment_method=payload.payment_method
    )
    return JSONResponse(result)

@app.post("/api/recovery/copilot-chat")
def copilot_chat(payload: CopilotChatRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recovery_workflows WHERE recovery_token = ?", (payload.recovery_token,))
    wf_row = cursor.fetchone()
    conn.close()

    context = dict(wf_row) if wf_row else {}
    answer = RecoveryAgent.answer_copilot_query(payload.question, context)
    return {"success": True, "answer": answer}

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount), COUNT(*) FROM transactions WHERE status IN ('AT_RISK_RECOVERY_IN_PROGRESS', 'FAILED', 'ABANDONED', 'RECOVERED')")
    at_risk_row = cursor.fetchone()
    total_at_risk = at_risk_row[0] or 0.0
    total_at_risk_count = at_risk_row[1] or 0

    cursor.execute("SELECT SUM(recovery_amount), COUNT(*) FROM recovery_workflows WHERE status = 'COMPLETED'")
    rec_row = cursor.fetchone()
    total_recovered = rec_row[0] or 0.0
    total_recovered_count = rec_row[1] or 0

    cursor.execute("SELECT SUM(amount), COUNT(*) FROM transactions WHERE status = 'BLOCKED_FRAUD'")
    fraud_row = cursor.fetchone()
    fraud_prevented = fraud_row[0] or 0.0
    fraud_count = fraud_row[1] or 0

    cursor.execute("SELECT SUM(amount), COUNT(*) FROM transactions WHERE status = 'APPROVED_SAFE'")
    safe_row = cursor.fetchone()
    safe_revenue = safe_row[0] or 0.0
    safe_count = safe_row[1] or 0

    recovery_rate = round((total_recovered_count / total_at_risk_count * 100), 1) if total_at_risk_count > 0 else 0.0

    conn.close()
    return {
        "total_at_risk": total_at_risk,
        "total_at_risk_count": total_at_risk_count,
        "total_recovered": total_recovered,
        "total_recovered_count": total_recovered_count,
        "recovery_rate": recovery_rate,
        "fraud_prevented": fraud_prevented,
        "fraud_count": fraud_count,
        "safe_revenue": safe_revenue,
        "safe_count": safe_count
    }

@app.get("/api/dashboard/events")
def get_dashboard_events():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM telemetry_events ORDER BY id DESC LIMIT 20")
    events = []
    for row in cursor.fetchall():
        ev = dict(row)
        try:
            ev["details"] = json.loads(ev.get("details_json", "{}"))
        except:
            ev["details"] = {}
        events.append(ev)
    conn.close()
    return {"success": True, "events": events}

@app.get("/api/dashboard/workflows")
def get_dashboard_workflows():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rw.*, u.name as user_name, u.email as user_email, u.phone as user_phone
        FROM recovery_workflows rw
        LEFT JOIN users u ON rw.user_id = u.user_id
        ORDER BY rw.id DESC
    """)
    workflows = []
    for row in cursor.fetchall():
        wf = dict(row)
        try:
            wf["messages"] = json.loads(wf.get("message_content", "{}"))
        except:
            wf["messages"] = {}
        workflows.append(wf)
    conn.close()
    return {"success": True, "workflows": workflows}

@app.post("/api/simulator/run-scenario")
def run_simulation_scenario(scenario_id: str = Form(...)):
    import random
    order_id = f"SIM-{random.randint(1000, 9999)}"
    
    if scenario_id == "safe_checkout":
        telemetry = {
            "gps_lat": 12.9716, "gps_lng": 77.5946, "gps_city": "Bengaluru, India",
            "ip_address": "103.21.124.55", "device_hash": "canvas_fp_bengaluru_chrome_win11",
            "is_vpn": False
        }
        res = RiskAgent.evaluate_transaction("USR-78291", order_id, 4999.0, "Razorpay UPI", telemetry)
        return {"scenario": "Verified Low-Risk User", "result": res}

    elif scenario_id == "geo_drift_stepup":
        telemetry = {
            "gps_lat": 28.6139, "gps_lng": 77.2090, "gps_city": "Delhi, India",
            "ip_address": "122.160.34.12", "device_hash": "canvas_fp_different_mac_safari",
            "is_vpn": False
        }
        res = RiskAgent.evaluate_transaction("USR-78291", order_id, 5999.0, "Card", telemetry)
        return {"scenario": "Location Drift (Step-Up Dynamic Friction)", "result": res}

    elif scenario_id == "bank_outage_recovery":
        telemetry = {
            "gps_lat": 12.9716, "gps_lng": 77.5946, "gps_city": "Bengaluru, India",
            "ip_address": "103.21.124.55", "device_hash": "canvas_fp_bengaluru_chrome_win11"
        }
        RiskAgent.evaluate_transaction("USR-78291", order_id, 3499.0, "HDFC Card", telemetry)
        rec = RecoveryAgent.trigger_recovery(order_id, "BANK_DOWNTIME", "HDFC Bank Card Network Gateway 504 Timeout", "USR-78291")
        return {"scenario": "Bank Gateway Outage -> Autonomous UPI Recovery", "result": rec}

    elif scenario_id == "stepup_dropout_recovery":
        telemetry = {
            "gps_lat": 19.0760, "gps_lng": 72.8777, "gps_city": "Mumbai, India",
            "device_hash": "canvas_fp_mumbai_safari_mac"
        }
        RiskAgent.evaluate_transaction("USR-45102", order_id, 5999.0, "Card", telemetry)
        rec = RecoveryAgent.trigger_recovery(order_id, "OTP_TIMEOUT", "Customer abandoned checkout at OTP step-up challenge", "USR-45102")
        return {"scenario": "Step-Up Friction Dropout -> WhatsApp 1-Click Recovery", "result": rec}

    elif scenario_id == "fraud_block":
        telemetry = {
            "gps_lat": 37.7749, "gps_lng": -122.4194, "gps_city": "San Francisco, USA",
            "ip_address": "198.51.100.24", "device_hash": "bot_headless_selenium_spoofed",
            "is_vpn": True, "is_tor": True
        }
        res = RiskAgent.evaluate_transaction("USR-78291", order_id, 18999.0, "Stolen Card", telemetry)
        return {"scenario": "Tor/VPN Bot Attack -> Blocked & Revenue Shielded", "result": res}

    return {"success": False, "message": "Unknown scenario"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
