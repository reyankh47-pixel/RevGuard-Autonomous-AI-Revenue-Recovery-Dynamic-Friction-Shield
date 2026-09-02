import sqlite3
import json
import uuid
from datetime import datetime
try:
    from .config import DB_PATH
except ImportError:
    from core.config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            gov_id_type TEXT DEFAULT 'Aadhaar / Driving License',
            gov_id_number TEXT,
            biometric_hash TEXT,
            kyc_status TEXT DEFAULT 'VERIFIED',
            gps_lat REAL DEFAULT 12.9716,
            gps_lng REAL DEFAULT 77.5946,
            gps_city TEXT DEFAULT 'Bengaluru, India',
            ip_address TEXT DEFAULT '103.21.124.55',
            device_hash TEXT DEFAULT 'canvas_fp_bengaluru_chrome_win11',
            risk_baseline REAL DEFAULT 8.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT,
            description TEXT,
            stock INTEGER DEFAULT 50
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            user_id TEXT,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            risk_score REAL DEFAULT 0.0,
            telemetry_json TEXT,
            explainable_ai_log TEXT,
            failure_reason TEXT,
            failure_detail TEXT,
            payment_method TEXT DEFAULT 'UPI / Card',
            items_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recovery_workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            order_id TEXT NOT NULL,
            user_id TEXT,
            recovery_token TEXT UNIQUE NOT NULL,
            strategy_type TEXT NOT NULL,
            original_amount REAL NOT NULL,
            recovery_amount REAL NOT NULL,
            discount_percent REAL DEFAULT 0.0,
            channel_dispatched TEXT NOT NULL,
            message_content TEXT,
            ai_rationale TEXT,
            recovery_probability REAL DEFAULT 80.0,
            attempts_count INTEGER DEFAULT 1,
            status TEXT DEFAULT 'TRIGGERED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            user_id TEXT,
            order_id TEXT,
            risk_score REAL,
            action_taken TEXT,
            details_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Apex Pro Smartwatch Ultra', 4999.0, 'Electronics', 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80', 'Aerospace-grade titanium case with live biometric telemetry & GPS.', 45),
            ('SonicWave Active Noise-Canceling Headphones', 3499.0, 'Audio', 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80', 'Spatial audio with 40-hour battery life and fast charging.', 60),
            ('Titan Stealth Mechanical Keyboard', 2899.0, 'Accessories', 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&q=80', 'Custom hot-swappable tactile switches with RGB lighting.', 30),
            ('PulseGuard Smart Fitness Ring', 5999.0, 'Wearables', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80', 'Sleep staging, skin temperature, and 24/7 heart recovery tracking.', 25),
            ('AeroPack Waterproof Travel Backpack', 1999.0, 'Gear', 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80', 'Ergonomic water-resistant 35L compartment with USB pass-through.', 70),
            ('CyberVision 4K Ultra-Wide Monitor Lightbar', 1499.0, 'Workspace', 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500&q=80', 'Asymmetric optical glare-free desk lamp with wireless puck controller.', 50)
        ]
        cursor.executemany('INSERT INTO products (name, price, category, image_url, description, stock) VALUES (?, ?, ?, ?, ?, ?)', sample_products)
        conn.commit()

    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ('USR-78291', 'Aditya Sharma', 'aditya.sharma@example.com', '+91 98765 43210', 'Driving License', 'DL-0420190012345', 'sha256_face_hash_a8f93e', 'VERIFIED', 12.9716, 77.5946, 'Bengaluru, India', '103.21.124.55', 'canvas_fp_bengaluru_chrome_win11', 8.5),
            ('USR-45102', 'Priya Patel', 'priya.patel@example.com', '+91 98123 45678', 'Passport', 'P9842104', 'sha256_face_hash_77b31c', 'VERIFIED', 19.0760, 72.8777, 'Mumbai, India', '115.112.45.89', 'canvas_fp_mumbai_safari_mac', 12.0),
            ('USR-99384', 'Rahul Verma', 'rahul.verma@example.com', '+91 99887 76655', 'Aadhaar Card', '9842 1204 8831', 'sha256_face_hash_33c99a', 'VERIFIED', 28.6139, 77.2090, 'Delhi, India', '122.160.34.12', 'canvas_fp_delhi_firefox_win', 9.0)
        ]
        cursor.executemany('INSERT INTO users (user_id, name, email, phone, gov_id_type, gov_id_number, biometric_hash, kyc_status, gps_lat, gps_lng, gps_city, ip_address, device_hash, risk_baseline) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', sample_users)
        conn.commit()

    conn.close()

if __name__ == '__main__':
    init_db()
    print('Database initialized and seeded.')
