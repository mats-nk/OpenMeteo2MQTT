# Weather (OpenMeteo) and air quality information

Fetch weather and air quality information from Open Meteo and publish it to a MQTT broker.

There is two scripts, one for weather information and one for air quality information.

Both scripts shares the same configuration file `config.yaml`.

In the configuration file you can change some settings and it also has some translations for weather codes and wind direction (compas (16-point).

## Requirements

Python libraries:
```
requests
paho-mqtt
pyyaml
```

## Languages supported

- English
- Swedish

## `weather_to_mqtt.py`

This script will featch weather data from https://open-meteo.com/ and publish it to different MQTT topics, see table belov.

```
openmeteo/weather/temperature_2m
openmeteo/weather/relative_humidity_2m
openmeteo/weather/apparent_temperature
openmeteo/weather/is_day
openmeteo/weather/precipitation
openmeteo/weather/rain
openmeteo/weather/showers
openmeteo/weather/snowfall
openmeteo/weather/weather_code
openmeteo/weather/cloud_cover
openmeteo/weather/pressure_msl
openmeteo/weather/surface_pressure
openmeteo/weather/wind_speed_10m
openmeteo/weather/wind_direction_10m
openmeteo/weather/wind_direction_compass
openmeteo/weather/wind_gusts_10m
```

## `air_quality_and_pollen_to_mqtt.py`

This script will featch air quality data from https://open-meteo.com/ and publish it to different MQTT topics, see table belov.

```
openmeteo//air/pm10
openmeteo//air/pm2_5
openmeteo//air/carbon_monoxide
openmeteo//air/nitrogen_dioxide
openmeteo//air/sulphur_dioxide
openmeteo//air/ozone
openmeteo//air/european_aqi
openmeteo//air/us_aqi

openmeteo//air/pollen_alder
openmeteo//air/pollen_birch
openmeteo//air/pollen_grass
openmeteo//air/pollen_mugwort
openmeteo//air/pollen_olive
openmeteo//air/pollen_ragweed

openmeteo//air/json
```

## `config.yaml`

```
location:
  latitude: 59.3294    # Stockholm
  longitude: 18.0687

open_meteo:
  endpoint: "https://api.open-meteo.com/v1/forecast"

mqtt:
  broker: "127.0.0.1"
  port: 1883
  base_topic_weather: "openmeteo/weather"
  base_topic_air: "openmeteo/air"
  client_id: "openmeteo_publisher"
  username: "mqtt1"   # null or a string
  password: "mqtt1"   # null or a string
  retain: true
  keepalive: 60

units:
  windspeed: "ms"
  temperature: "celsius"

publish:
  interval_seconds: 600

air_quality:
  enabled: true

language:
  compass: en
  weather: en

compass:
  sv:
    - N
    - NNO
    - NO
    - ONO
    - O
    - OSO
    - SO
    - SSO
    - S
    - SSV
    - SV
    - VSV
    - V
    - VNV
    - NV
    - NNV

  en:
    - N
    - NNE
    - NE
    - ENE
    - E
    - ESE
    - SE
    - SSE
    - S
    - SSW
    - SW
    - WSW
    - W
    - WNW
    - NW
    - NNW

weather_code:
  sv:
    0: Klart
    1: Mest klart
    2: Delvis molnigt
    3: Mulet
    45: Dimma
    48: Rimfrostdimma
    51: Lätt duggregn
    53: Måttligt duggregn
    55: Kraftigt duggregn
    56: Lätt underkylt duggregn
    57: Kraftigt underkylt duggregn
    61: Lätt regn
    63: Måttligt regn
    65: Kraftigt regn
    66: Lätt underkylt regn
    67: Kraftigt underkylt regn
    71: Lätt snöfall
    73: Måttligt snöfall
    75: Kraftigt snöfall
    77: Snökorn
    80: Lätta regnskurar
    81: Måttliga regnskurar
    82: Kraftiga regnskurar
    85: Lätta snöbyar
    86: Kraftiga snöbyar
    95: Åska
    96: Åska med lätt hagel
    99: Åska med kraftigt hagel

  en:
    0: Clear sky
    1: Mainly clear
    2: Partly cloudy
    3: Overcast
    45: Fog
    48: Depositing rime fog
    51: Light drizzle
    53: Moderate drizzle
    55: Dense drizzle
    56: Light freezing drizzle
    57: Dense freezing drizzle
    61: Slight rain
    63: Moderate rain
    65: Heavy rain
    66: Light freezing rain
    67: Heavy freezing rain
    71: Slight snow fall
    73: Moderate snow fall
    75: Heavy snow fall
    77: Snow grains
    80: Slight rain showers
    81: Moderate rain showers
    82: Violent rain showers
    85: Slight snow showers
    86: Heavy snow showers
    95: Thunderstorm
    96: Thunderstorm with slight hail
    99: Thunderstorm with heavy hail
```

