# RetroWoT Middleware
This repository contains a Proof of Concept for a middleware to generate for legacy IoT devices (currently Bluetooth LE and ZigBee) a Web of Things Thing Description. 
It is designed with different components to be easily extensible.


## Features
- Supports the generation of Thing Descriptions (TDs) for Bluetooth LE and ZigBee devices.
- Supports pushing new TDs to a Thing Directory
- Allow access via HTTP or CoAP to the device
- Extends the interaction affordances with additional forms for HTTP or CoAP

## Installation
1. Ensure you have poetry and python installed. The software has been tested on Ubuntu 22.04 LTS.
2. Clone the repository
3. Install the requirements (necessary python packages with):
``` 
poetry install
```
## Usage
1. To start the RetroWoT run:
```
python main.py
```
2. The server should now be accessible over `localhost:8000`.
3. To search for new devices run for Bluetooth `localhost:8000/bluetooth/device_discovery` and for Zigbee `localhost:8000/zigbee/device_discovery`
    - Note: You may have to activate the pairing mode on the ZigBee and/or Bluetooth device to be accessible by the environment.
4. A list of all discovered devices should appear after a while (10-15 seconds)
5. Select your address of your device and run `localhost:8000/bluetooth/service_discovery/$ADDRESS$` or `localhost:8000/zigbee/service_discovery/$ADDRESS$`.

## Demo

## Contributing
Contributions to improve the LIG-WoT are welcome. Please feel free to submit pull requests or open issues to discuss potential improvements or report bugs.