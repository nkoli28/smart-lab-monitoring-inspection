import json, logging, random, threading
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from app.anomaly import detect_anomalies
from app.config import MQTT_HOST, MQTT_PORT, MQTT_TOPIC, SIMULATOR_INTERVAL_SECONDS
from app.database import Alert, Reading, SessionLocal
logger = logging.getLogger(__name__)
_stop = threading.Event()
_client = None

def _on_connect(client, _userdata, _flags, reason_code, _properties=None):
    if reason_code == 0: client.subscribe(MQTT_TOPIC); logger.info("Subscribed to %s", MQTT_TOPIC)
    else: logger.error("MQTT connection failed: %s", reason_code)

def _on_message(_client, _userdata, message):
    db: Session = SessionLocal()
    try:
        p = json.loads(message.payload.decode("utf-8")); sid = str(p.get("sensor_id", "sensor-unknown"))
        temp, vib = float(p["temperature_c"]), float(p["vibration"])
        db.add(Reading(sensor_id=sid, temperature_c=temp, vibration=vib, equipment_status=str(p.get("equipment_status", "simulated")), recorded_at=datetime.now(timezone.utc)))
        for reason in detect_anomalies(temp, vib): db.add(Alert(sensor_id=sid, severity="warning", message=reason, temperature_c=temp, vibration=vib, created_at=datetime.now(timezone.utc)))
        db.commit()
    except (ValueError, KeyError, TypeError, json.JSONDecodeError): db.rollback(); logger.warning("Ignoring invalid MQTT payload")
    except Exception: db.rollback(); logger.exception("Telemetry persistence failed")
    finally: db.close()

def start_mqtt():
    global _client
    _stop.clear(); _client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="smart-lab-api")
    _client.on_connect, _client.on_message = _on_connect, _on_message
    _client.connect_async(MQTT_HOST, MQTT_PORT, keepalive=30); _client.loop_start()

def stop_mqtt():
    _stop.set()
    if _client is not None: _client.loop_stop(); _client.disconnect()

def run_sensor_simulator():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="smart-lab-simulator")
    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=30); client.loop_start(); n = 0
        while not _stop.wait(max(0.5, SIMULATOR_INTERVAL_SECONDS)):
            n += 1; abnormal = n % 10 == 0
            payload = {"sensor_id":"lab-sensor-01", "temperature_c":round(random.uniform(33,36) if abnormal else random.uniform(21,29),2), "vibration":round(random.uniform(.9,1.2) if abnormal else random.uniform(.05,.5),3), "equipment_status":"simulated", "timestamp":datetime.now(timezone.utc).isoformat()}
            client.publish("lab/sensors/lab-sensor-01", json.dumps(payload), qos=1)
    except Exception: logger.exception("Sensor simulator stopped")
    finally: client.loop_stop(); client.disconnect()
