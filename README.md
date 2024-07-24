# RetroWoT - A Method to Retrofit Legacy Devices for the Web of Things

## Introduction
This repository contains additional information about RetroWoT. 
RetroWoT is a method and a middleware to automatically generate Thing Descriptions for legacy IoT devices. 
The primary goal of RetroWoT is to provide a solution to integrate the billions of existing devices [1] into the Web of Things [2]. 
The Web of Things is a open standard that enables interoperability across IoT platforms, stacks, and application, by providing Thing Descriptions [3] as interface descriptions for devices and Thing Description Directories [4] for a more simplified discovery of devices. 

To enable it, we rely on often used discovery protocols for device identification and service discovery. 
Many IoT stacks (e.g. Bluetooth LE, ZigBee, or Matter) use these types of discovery protocols to create a network between IoT devices using the same protocol stack.
Thus they enable interoperability within an instantiated network (Think e.g. about your own home as such a network).

In this repository we provide:
- [RetroWoT Middleware](./implementation/README.md): Our implementation that uses the discovery protocols of Bluetooth LE and ZigBee, and the ontology to create a Thing Description for a Bluetooth LE or ZigBee device.
- [RetroWoT Evaluation](./evaluation/README.md): Scripts and results of the effectiveness and performance evaluation for our approach.  


## License
Specify the license under which your research project is released. Include any relevant copyright or attribution information.

## References
- [1] Bluetooth Report: https://www.bluetooth.com/de/2024-market-update/
- [2] Web of Things: https://www.w3.org/TR/wot-architecture11/
- [3] Thing Descriptions: https://www.w3.org/TR/wot-thing-description11/
- [4] Thing Description Directory: https://www.w3.org/TR/wot-discovery/


## Contact
Provide contact information for yourself or your team, in case others have questions or want to collaborate.
