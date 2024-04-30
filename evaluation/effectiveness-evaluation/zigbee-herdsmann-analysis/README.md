# Data Analysis for ZigBee2MQTT
This script contains a copy of the ZigBee-Herdsman-Converter [1] used by ZigBee2MQTT [2] to translate data from ZigBee to MQTT.
Zigbee2MQTT is used in home automation solutions and contains a list of device models collected and integrated into home automation solutions by the community around Home Assistant, Homey, Domoticz, and IoBroker.

## Installation
1. Ensure you have poetry and python installed. The software has been tested on Ubuntu 22.04 LTS.
2. Install the requirements (necessary python packages with):
``` 
poetry install
```
## Usage
To start the data extraction run the following commands:
```
poetry shell
```

Run the Python Notebook to see how to extract the raw data:
```
./zigbee-herdsman-converter-analysis.ipynb
```


## References
- [1] ZigBee Herdsman Converter: https://github.com/koenkk/zigbee-herdsman-converters
- [2] ZigBee2MQTT: https://github.com/Koenkk/zigbee2mqtt

