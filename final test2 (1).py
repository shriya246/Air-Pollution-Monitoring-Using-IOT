import sys
sys.path.insert(0, '/home/shriyapatel/myenv/lib/python3.11/site-packages')

import time
import board
import busio
import json
import warnings
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

warnings.filterwarnings("ignore")

class ADS:
    P0 = 0  
    P1 = 1  


VCC = 5.0
RL = 10000
R0_MQ7 = 10000
R0_MQ135 = 10000
THRESHOLD_MQ7 = 2.5
THRESHOLD_MQ135 = 1.8


i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
chan_mq7 = AnalogIn(ads, ADS.P0)
chan_mq135 = AnalogIn(ads, ADS.P1)


mqtt_client = AWSIoTMQTTClient("MyIotThing")
mqtt_client.configureEndpoint("a2yesy1d5bejhy-ats.iot.us-east-2.amazonaws.com", 8883)
mqtt_client.configureCredentials("Amazon-root-CA-1.pem", "private.pem.key", "device.cert.pem")
mqtt_client.connect()


COMMAND_TOPIC = "gasmonitor/data"
DATA_TOPIC = "gasmonitor/data"
ALERT_TOPIC = "gasmonitor/alert"


monitoring = False
mq7_alert_sent = False
mq135_alert_sent = False

def calculate_rs(voltage):
    return ((VCC - voltage) * RL) / voltage if voltage != 0 else float('inf')


def command_callback(client, userdata, message):
    global monitoring
    try:
        payload = json.loads(message.payload.decode())
        command = payload.get("message", "").strip().lower()

        if command == "start reading":
            monitoring = True
            print("Monitoring started.")
        elif command == "stop reading":
            monitoring = False
            print("Monitoring stopped.")
    except Exception as e:
        print("Error parsing MQTT command:", e)


mqtt_client.subscribe(COMMAND_TOPIC, 1, command_callback)


try:
    print("Waiting for MQTT command: 'start reading' or 'stop reading'...")

    while True:
        if monitoring:
            
            v_mq7 = chan_mq7.voltage
            v_mq135 = chan_mq135.voltage

            
            rs_mq7 = calculate_rs(v_mq7)
            rs_mq135 = calculate_rs(v_mq135)
            rsr0_mq7 = rs_mq7 / R0_MQ7
            rsr0_mq135 = rs_mq135 / R0_MQ135


            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            
            payload = {
                "mq7_voltage": v_mq7,
                "mq135_voltage": v_mq135,
                "rsr0_mq7": rsr0_mq7,
                "rsr0_mq135": rsr0_mq135,
                "timestamp": timestamp
            }
            mqtt_client.publish(DATA_TOPIC, json.dumps(payload), 1)
           

            
            if rsr0_mq7 < THRESHOLD_MQ7 and not mq7_alert_sent:
                alert_payload = {
                    "sensor": "MQ-7",
                    "type": "CO",
                    "rsr0": rsr0_mq7,
                    "timestamp": timestamp
                }
                mqtt_client.publish(ALERT_TOPIC, json.dumps(alert_payload), 1)
                print("CO Alert sent.")
                mq7_alert_sent = True
            elif rsr0_mq7 >= THRESHOLD_MQ7:
                mq7_alert_sent = False

            if rsr0_mq135 < THRESHOLD_MQ135 and not mq135_alert_sent:
                alert_payload = {
                    "sensor": "MQ-135",
                    "type": "CO2",
                    "rsr0": rsr0_mq135,
                    "timestamp": timestamp
                }
                mqtt_client.publish(ALERT_TOPIC, json.dumps(alert_payload), 1)
                print("CO2 Alert sent.")
                mq135_alert_sent = True
            elif rsr0_mq135 >= THRESHOLD_MQ135:
                mq135_alert_sent = False

            time.sleep(10)
        else:
            time.sleep(1)

except KeyboardInterrupt:
     print("Script interrupted by user.")