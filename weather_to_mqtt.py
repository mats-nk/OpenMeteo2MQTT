import time
import json
import yaml
import argparse
import requests
import paho.mqtt.client as mqtt


# -------------------------------------------------
# Load configuration
# -------------------------------------------------
with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

LAT = cfg["location"]["latitude"]
LON = cfg["location"]["longitude"]

MQTT_CFG = cfg["mqtt"]
PUBLISH_INTERVAL = cfg["publish"]["interval_seconds"]
RETAIN = MQTT_CFG.get("retain", True)

WIND = cfg["units"]["windspeed"]


# -------------------------------------------------
# Open-Meteo URL (unit-aware)
# -------------------------------------------------
WEATHER_URL = (
    f'{cfg["open_meteo"]["endpoint"]}'
    f'?latitude={LAT}'
    f'&longitude={LON}'
    f'&current_weather=true'
    f'&windspeed_unit={WIND}'
)


# -------------------------------------------------
# MQTT callbacks (API v2)
# -------------------------------------------------
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT connected")
    else:
        print(f"MQTT connection failed: {reason_code}")

def on_disconnect(client, userdata, flags, reason_code, properties):
    print(f"MQTT disconnected (reason: {reason_code})")


# -------------------------------------------------
# MQTT client setup
# -------------------------------------------------
client = mqtt.Client(
    client_id=MQTT_CFG["client_id"],
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

if MQTT_CFG.get("username"):
    client.username_pw_set(
        MQTT_CFG["username"],
        MQTT_CFG["password"]
    )

client.connect(
    MQTT_CFG["broker"],
    MQTT_CFG["port"],
    keepalive=MQTT_CFG.get("keepalive", 60)
)


# -------------------------------------------------
# Weather fetch
# -------------------------------------------------
def fetch_weather():
    response = requests.get(WEATHER_URL, timeout=10)
    response.raise_for_status()
    return response.json()["current_weather"]


# -------------------------------------------------
# Publish weather data
# -------------------------------------------------
def publish_weather():
    weather = fetch_weather()

    payload = {
        "temperature": weather.get("temperature"),
        "windspeed": weather.get("windspeed"),
        "winddirection": weather.get("winddirection"),
        "weathercode": weather.get("weathercode"),
        "time": weather.get("time"),
    }

    base_topic = MQTT_CFG["base_topic"]

    for key, value in payload.items():
        client.publish(
            f"{base_topic}/{key}",
            value,
            retain=RETAIN
        )

    client.publish(
        f"{base_topic}/json",
        json.dumps(payload),
        retain=RETAIN
    )

    print("Published:", payload)


# -------------------------------------------------
# Main loop
# -------------------------------------------------
if __name__ == "__main__":
    try:
        client.loop_start()
        while True:
            publish_weather()
            time.sleep(PUBLISH_INTERVAL)
    except KeyboardInterrupt:
        print("Stopping publisher...")
    finally:
        client.loop_stop()
        client.disconnect()

