# weather_to_mqtt.py
# ------------------
# Fetch weather information from Open Meteo and publish it to a MQTT broker.
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

WIND = cfg["units"]["windspeed"]

COMPASS_LANG = cfg.get("language", {}).get("compass", "sv")
WEATHER_LANG = cfg.get("language", {}).get("weather", "sv")

COMPASS_MAP = cfg.get("compass", {})
WEATHER_CODE_MAP = cfg.get("weather_code", {})

# -------------------------------------------------
# Open-Meteo URL
# -------------------------------------------------
WEATHER_URL = (
    f'{cfg["open_meteo"]["endpoint"]}'
    f'?latitude={LAT}'
    f'&longitude={LON}'
    f'&current='
    f'temperature_2m,relative_humidity_2m,apparent_temperature,is_day,'
    f'precipitation,rain,showers,snowfall,weather_code,cloud_cover,'
    f'pressure_msl,surface_pressure,'
    f'wind_speed_10m,wind_direction_10m,wind_gusts_10m'
    f'&windspeed_unit={WIND}'
)

# -------------------------------------------------
# Conversions
# -------------------------------------------------
def degrees_to_compass(deg):
    if deg is None:
        return None

    directions = COMPASS_MAP.get(COMPASS_LANG)
    if not directions or len(directions) != 16:
        raise ValueError(f"Compass language '{COMPASS_LANG}' must contain 16 values")

    idx = int((deg + 11.25) / 22.5) % 16
    return directions[idx]


def weather_code_to_text(code):
    if code is None:
        return None

    lang_map = WEATHER_CODE_MAP.get(WEATHER_LANG, {})
    return lang_map.get(code, f"Unknown ({code})")

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
# Fetch weather
# -------------------------------------------------
def fetch_weather():
    r = requests.get(WEATHER_URL, timeout=10)
    r.raise_for_status()
    return r.json()["current"]

# -------------------------------------------------
# Publish weather
# -------------------------------------------------
def publish_weather():
    weather = fetch_weather()

    wind_deg = weather.get("wind_direction_10m")
    weather_code = weather.get("weather_code")

    payload = {
        "temperature_2m": weather.get("temperature_2m"),
        "relative_humidity_2m": weather.get("relative_humidity_2m"),
        "apparent_temperature": weather.get("apparent_temperature"),
        "is_day": weather.get("is_day"),
        "precipitation": weather.get("precipitation"),
        "rain": weather.get("rain"),
        "showers": weather.get("showers"),
        "snowfall": weather.get("snowfall"),
        "weather_code": weather_code,
        "weather_description": weather_code_to_text(weather_code),
        "cloud_cover": weather.get("cloud_cover"),
        "pressure_msl": weather.get("pressure_msl"),
        "surface_pressure": weather.get("surface_pressure"),
        "wind_speed_10m": weather.get("wind_speed_10m"),
        "wind_direction_10m": wind_deg,
        "wind_direction_compass": degrees_to_compass(wind_deg),
        "wind_gusts_10m": weather.get("wind_gusts_10m"),
        "time": weather.get("time"),
    }

    base = MQTT_CFG["base_topic_weather"]

    for k, v in payload.items():
        client.publish(f"{base}/{k}", v, retain=RETAIN)

    client.publish(f"{base}/json", json.dumps(payload), retain=RETAIN)

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
        print("Stopping…")
    finally:
        client.loop_stop()
        client.disconnect()
