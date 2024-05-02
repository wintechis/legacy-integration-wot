# Data Analysis for ZigBee2MQTT
This script contains a copy of the ZigBee-Herdsman-Converter [1] used by ZigBee2MQTT [2] to translate data from ZigBee to MQTT.
Zigbee2MQTT is used in home automation solutions and contains a list of device models collected manually and integrated into home automation solutions by the community around Home Assistant, Homey, Domoticz, and IoBroker.

The community around Zigbee2MQTT defines for each device model external definitions [3]. 
The external definitions specify which clusters are available for a specific device. 
Furthermore, they also show which clusters are defined following the standard, and which not.
A cluster in the context of RetroWoT is a set of service capabilities, thus allowing a estimation about the effectiveness of the service capability enrichment.

An example of such a external definition is shown below:
```
const definition = {
    zigbeeModel: ['lumi.sens'],
    model: 'WSDCGQ01LM',
    vendor: 'Xiaomi',
    description: 'MiJia temperature & humidity sensor',
    extend: [],
    fromZigbee: [fz.temperature], // <-- added here all clusters reported from zigbee
    toZigbee: [], // <-- add here all clusters to send commands to zigbee
    exposes: [e.battery(), e.temperature(), e.humidity()], // <-- this will define which fields will be exposed in the definition message to configure a frontend (e.g. the Z2M frontend, Home Assistant, Domoticz)
};
```



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
- [3] Zigbee2MQTT External definitions: https://www.zigbee2mqtt.io/advanced/support-new-devices/01_support_new_devices.html#_2-creating-the-external-definition