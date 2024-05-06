# Bluetooth Field Analysis

This documentation provides the process to analyze the data for brownfield devices for the IoT Protocol Bluetooth LE.
To analyze the usage of discovery protocols, we created a script that discovers devices and extracts their service capabilities that is visualized as a pipeline in the following figure. 
For the automation of the pipeline we run a cron-job every 15 minutes.

<img src="./bluetooth field analysis procedure.png" width="100%" alt="description">

- Discover devices: All Devices in the current environment are identified.
- Filter out already discovered devices: For each device that has been identified, the script checks if the device has already been seen. If its the case the already discovered device is not been further processed.
- Save discovered devices: The newly discovered devices are then stored first in a dictonary and then in a separate document.
- Try to connect: For each new device a request to the device for service discovery is made. If the device is connectable a connection is established to the device.
- Discover services: All services of a device are retrieved and stored in a document. The results are then analysed in a separate script.

## Installation
To run the scripts use the copy of the service_discovery.py in the retrowot implementation under `/implementation/retrowot/retrowot/service_discover.py`.

To use the script a separate USB-dongle is required and made accessible as described [here](../../../implementation/README.md#installation).

The results from the scanning are stored in the folder `experiments`.

The results can then be analyzed with the Jupyter Notebook:
```
./evaluation.ipynb
```
