from app.config import TEMP_THRESHOLD_C, VIBRATION_THRESHOLD

def detect_anomalies(temperature_c: float, vibration: float, temperature_threshold: float = TEMP_THRESHOLD_C, vibration_threshold: float = VIBRATION_THRESHOLD) -> list[str]:
    """Return human-readable anomaly reasons for simulated sensor values."""
    reasons = []
    if temperature_c > temperature_threshold:
        reasons.append(f"Temperature {temperature_c:.1f} C exceeds threshold {temperature_threshold:.1f} C")
    if vibration > vibration_threshold:
        reasons.append(f"Vibration {vibration:.2f} exceeds threshold {vibration_threshold:.2f}")
    return reasons
