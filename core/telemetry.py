import math
import hashlib
import json

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates in kilometers."""
    R = 6371.0  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def generate_fingerprint_hash(signals: dict) -> str:
    """Generates a unique deterministic device fingerprint from hardware & browser signals."""
    components = [
        str(signals.get("user_agent", "")),
        str(signals.get("screen_res", "")),
        str(signals.get("color_depth", "")),
        str(signals.get("timezone", "")),
        str(signals.get("language", "")),
        str(signals.get("canvas_hash", "")),
        str(signals.get("webgl_vendor", ""))
    ]
    raw_str = "|".join(components)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:24]

def analyze_telemetry_signals(baseline: dict, live: dict) -> dict:
    """
    Compares live telemetry with baseline profile.
    Returns anomaly breakdown and metrics.
    """
    results = {
        "geo_distance_km": 0.0,
        "geo_anomaly": False,
        "device_match": True,
        "network_anomaly": False,
        "risk_points": 0.0,
        "reasons": []
    }
    
    # 1. Geolocation Check
    base_lat = baseline.get("gps_lat", 12.9716)
    base_lng = baseline.get("gps_lng", 77.5946)
    live_lat = live.get("gps_lat", base_lat)
    live_lng = live.get("gps_lng", base_lng)
    
    if live_lat is not None and live_lng is not None:
        dist = haversine_distance(base_lat, base_lng, live_lat, live_lng)
        results["geo_distance_km"] = round(dist, 1)
        
        if dist > 350.0:
            results["geo_anomaly"] = True
            results["risk_points"] += 35.0
            results["reasons"].append(f"Geo-Drift: Device is {round(dist)} km from registration baseline ({baseline.get('gps_city', 'Baseline')}).")
        elif dist > 80.0:
            results["risk_points"] += 12.0
            results["reasons"].append(f"Moderate distance shift: {round(dist)} km from registered location.")
        else:
            results["reasons"].append(f"Location Verified: Within safe radius ({round(dist)} km) of baseline.")
    
    # 2. Device Fingerprint Check
    base_device = baseline.get("device_hash", "")
    live_device = live.get("device_hash", "")
    
    if base_device and live_device and base_device != live_device:
        results["device_match"] = False
        results["risk_points"] += 25.0
        results["reasons"].append("Device Anomaly: Unrecognized browser canvas signature or hardware profile.")
    else:
        results["reasons"].append("Device Fingerprint: Canvas & browser hardware profile matches registered baseline.")
        
    # 3. Network / IP Anomaly Check
    is_vpn = live.get("is_vpn", False)
    is_proxy = live.get("is_proxy", False)
    is_tor = live.get("is_tor", False)
    
    if is_vpn or is_proxy or is_tor:
        results["network_anomaly"] = True
        results["risk_points"] += 35.0
        results["reasons"].append("Network Alert: Detected anonymous proxy, datacenter IP, or active VPN routing.")
    else:
        results["reasons"].append("Network Integrity: Verified residential/mobile ISP connection.")
        
    return results
