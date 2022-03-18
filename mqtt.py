import paho.mqtt.client as mqtt


MQTT_URL = "localhost"
QOS_LEVEL = 2
TOPIC_TEMP_ENV = "main/sensor/temp_evn"
TOPIC_HUMIDITY = "main/senosr/humidity"
TOPIC_TEMP_PROC = "main/sensor/temp_proc"
TOPIC_PRESSURE = "main/senosr/pressure"
TOPIC_VOLTAGE = "main/senosr/voltage"
TOPIC_LIGHT = "main/senosr/light"
TOPIC_PI_TEMP = "main/mqtt/temperature"

topics = [(TOPIC_TEMP_ENV, QOS_LEVEL),
        (TOPIC_HUMIDITY, QOS_LEVEL),
        (TOPIC_TEMP_PROC, QOS_LEVEL),
        (TOPIC_PRESSURE, QOS_LEVEL),
        (TOPIC_VOLTAGE, QOS_LEVEL),
        (TOPIC_LIGHT, QOS_LEVEL),
        (TOPIC_PI_TEMP, QOS_LEVEL)]