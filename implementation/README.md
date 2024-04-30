# RetroWoT Middleware
This repository contains a Proof of Concept for a middleware to generate for legacy IoT devices (currently Bluetooth LE and ZigBee) a Web of Things Thing Description. 
It is designed with different components to be easily extensible.


## Features
- Supports the generation of Thing Descriptions (TDs) for Bluetooth LE and ZigBee devices.
- Supports pushing new TDs to a Thing Directory
- Allow access via HTTP or CoAP to the device
- Extends the interaction affordances with additional forms for HTTP or CoAP

## Requirements
- For Bluetooth: A Bluetooth Dongle is required
- For ZigBee: A ZigBee Dongle such as the Sonoff Zigbee 3.0 USB Dongle Plus (Model: ZBDongle-E) is required

## Installation
1. Ensure you have poetry and python installed. The software has been tested on Ubuntu 22.04 LTS.
2. Clone the repository
3. Install the requirements (necessary python packages with):
``` 
poetry install
```
4. Identify the connection to the Dongle and ensure control rights for the device:
4.1. For Bluetooth: 
Identify the device, via:
``` 
lsusb
```
The result from the console should look like this:
```
Bus 001 Device 005: ID 5986:2118 ...
Bus 001 Device 023: ID 8087:0a2b ...
Bus 001 Device 025: ID 0a12:0001 Cambridge Silicon Radio, Ltd Bluetooth Dongle (HCI mode) <---- This is the Bluetooth USB Dongle
Bus 001 Device 027: ID 1a86:55d4 QinHeng Electronics SONOFF Zigbee 3.0 USB Dongle Plus V2 <---- This is the ZigBee USB Dongle
Bus 001 Device 026: ID 0d28:0204 ...
```

Ensure now admin rights to the device, via:
``` 
sudo chmod 666 /dev/bus/usb/001/025 
```

Set the environmental variable of the Bluetooth Dongle, via:
```
export BLUETOOTH_HCI_DEVICE_LINK='usb:0a12:0001' 
```
Note: The `0a12:0001` is the ID of the Bluetooth Dongle found via lsusb.


4.2. For ZigBee:

Go to /dev and look for ttyACMX or ttyUSBX.
By plugging the USB Dongle in and out the device should be findable. 
 

 Ensure now admin rights to the device, via:
``` 
sudo chmod 666 /dev/ttyACMX
```

Set the environmental variable of the Bluetooth Dongle, via:
```
export ZIGBEE_DEVICE_PATH = '/dev/ttyACMX'
```
Note: The `ttyACMX` or `ttyUSBX` is the link to the USB Dongle.



## Usage

### USAGE via Docker
1. Build all docker containers, via:
```
sudo docker-compose build 
```
2. Run docker-compose, via:
```
sudo docker-compose up 
```
3. Open a browser and call http://localhost:8501
4. (Optional) To access the Thing Description Directory open a browser and call http://localhost:9000


### Usage via Frontend
1. To start the RetroWoT run:
```
python main.py
```
2. In a new terminal run:
```
streamlit run app.py
```

### Usage via browser directly

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
The demonstrator showcases the functionality of RetroWoT for Bluetooth LE devices (but also implemented for ZigBee). 
- 1. Device Discovery: Surrounding devices are discovered and a user can select a given device (in the example a device with the address F3:82:06:2F:7C:0A)  
- 2. Service Discovery: The devices services are discovered and generalized with the SCO ontology for further processing and creation of the TD
- 3. Thing Descriptions: The Thing Description that is now accessible.
![](./demo.gif)
