# Air-Pollution-Monitoring-Using-IOT
## 🚀 How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/air-pollution-monitoring.git
cd air-pollution-monitoring
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup AWS IoT Certificates
Ensure you have the following certificate files from AWS IoT:
Amazon-root-CA-1.pem
device.cert.pem
private.pem.key
Place them in the same directory as air_monitoring.py.

### 4. Run the Monitoring Script
```bash
python air_monitoring.py
```

You can control the sensor monitoring by publishing the following MQTT commands to the gasmonitor/data topic:
"start reading" to begin monitoring
"stop reading" to halt it

📊 Project Summary
Uses MQ-7 (CO detection) and MQ-135 (CO₂ and other gases)
Sends real-time data and alert thresholds to AWS IoT Core
Publishes alerts to a specific topic when thresholds are breached
Calculates Rs/R0 ratios to determine pollution levels

🧰 Tech Stack
Python 3.11
Raspberry Pi (I2C interface)
Adafruit ADS1115
AWS IoT Core + MQTT
Sensors: MQ-7 and MQ-135

📜 License
This project is open-source and licensed under the MIT License.
"""
