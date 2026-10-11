import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartlab.db")
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "lab/sensors/#")
TEMP_THRESHOLD_C = float(os.getenv("TEMP_THRESHOLD_C", "32"))
VIBRATION_THRESHOLD = float(os.getenv("VIBRATION_THRESHOLD", "0.8"))
SIMULATOR_INTERVAL_SECONDS = float(os.getenv("SIMULATOR_INTERVAL_SECONDS", "3"))
