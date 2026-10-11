from app.anomaly import detect_anomalies

def test_normal_readings_have_no_anomalies():
    assert detect_anomalies(24.0, 0.2, 32.0, 0.8) == []

def test_high_temperature_is_detected():
    assert "Temperature" in detect_anomalies(35.0, 0.2, 32.0, 0.8)[0]

def test_high_vibration_is_detected():
    assert "Vibration" in detect_anomalies(24.0, 1.1, 32.0, 0.8)[0]

def test_both_thresholds_are_detected():
    assert len(detect_anomalies(35.0, 1.1, 32.0, 0.8)) == 2
