# air_quality_and_pollen_to_mqtt.py
# ---------------------------------
# Fetch air quality information from Open Meteo and publish it to a MQTT broker.
#
# Mats Karlsson 2026-02-09
#
import time
import json
import yaml
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

# -------------------------------------------------
# Open-Meteo Air Quality + Pollen URLs
# -------------------------------------------------
AIR_URL = (
    "https://air-quality-api.open-meteo.com/v1/air-quality"
    f"?latitude={LAT}"
    f"&longitude={LON}"
    "&current="
    "pm10,pm2_5,carbon_monoxide,"
    "nitrogen_dioxide,sulphur_dioxide,ozone,"
    "european_aqi,us_aqi"
)

POLLEN_URL = (
    "https://air-quality-api.open-meteo.com/v1/air-quality"
    f"?latitude={LAT}"
    f"&longitude={LON}"
    "&current="
    "alder_pollen,birch_pollen,grass_pollen,"
    "mugwort_pollen,olive_pollen,ragweed_pollen"
)

# -------------------------------------------------
# MQTT callbacks
# -------------------------------------------------
def on_connect(client, userdata, flags, reason_code, properties):
    print("MQTT connected" if reason_code == 0 else f"MQTT failed: {reason_code}")

def on_disconnect(client, userdata, flags, reason_code, properties):
    print(f"MQTT disconnected (reason: {reason_code})")

# -------------------------------------------------
# MQTT client setup
# -------------------------------------------------
client = mqtt.Client(
    client_id=MQTT_CFG["client_id"] + "_air_pollen",
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
# Fetchers
# -------------------------------------------------
def fetch_air_quality():
    r = requests.get(AIR_URL, timeout=10)
    r.raise_for_status()
    return r.json()["current"]

def fetch_pollen():
    r = requests.get(POLLEN_URL, timeout=10)
    r.raise_for_status()
    return r.json()["current"]

# -------------------------------------------------
# Publish air quality + pollen
# -------------------------------------------------
def publish_air_and_pollen():
    air = fetch_air_quality()
    pollen = fetch_pollen()

    payload = {
        # --- Air quality ---
        "pm10": air.get("pm10"),
        "pm2_5": air.get("pm2_5"),
        "carbon_monoxide": air.get("carbon_monoxide"),
        "nitrogen_dioxide": air.get("nitrogen_dioxide"),
        "sulphur_dioxide": air.get("sulphur_dioxide"),
        "ozone": air.get("ozone"),
        "european_aqi": air.get("european_aqi"),
        "us_aqi": air.get("us_aqi"),

        # --- Pollen ---
        "pollen_alder": pollen.get("alder_pollen"),
        "pollen_birch": pollen.get("birch_pollen"),
        "pollen_grass": pollen.get("grass_pollen"),
        "pollen_mugwort": pollen.get("mugwort_pollen"),
        "pollen_olive": pollen.get("olive_pollen"),
        "pollen_ragweed": pollen.get("ragweed_pollen"),

        # --- Timestamp ---
        "time": air.get("time") or pollen.get("time"),
    }

    base = MQTT_CFG["base_topic_air"]

    for k, v in payload.items():
        client.publish(f"{base}/{k}", v, retain=RETAIN)

    client.publish(
        f"{base}/json",
        json.dumps(payload),
        retain=RETAIN
    )

    print("Published air quality + pollen:", payload)

# -------------------------------------------------
# Main loop
# -------------------------------------------------
if __name__ == "__main__":
    try:
        client.loop_start()
        while True:
            publish_air_and_pollen()
            time.sleep(PUBLISH_INTERVAL)
    except KeyboardInterrupt:
        print("Stopping air & pollen publisher…")
    finally:
        client.loop_stop()
        client.disconnect()
