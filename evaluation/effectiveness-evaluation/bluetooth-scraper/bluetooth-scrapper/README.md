# Data Scrapper for Bluetooth LE 
This script contains the different components to extract bluetooth device information from the Bluetooth Listing Database. 

The Bluetooth Listing Database [1] is the official repository of Bluetooth SIG for qualified designs and declard products.
Hence, the database contains a large, cross-domain dataset maintained by an official standardization organization.
The data from the database contains information about device types (all qualified designs and declared products), their qualification level towards a specific features, such as the conformance to a service/profile.


A service/profile in the context of RetroWoT is a set of service capabilities, thus allowing a estimation about the effectiveness of the service capability enrichment.


## Methodology

- Extract with a script all device models from the database
- Look up details about the conformance to services and profiles supported by Bluetooth LE.
- Extract the relevant information for the analysis of the enrichment procedure and the conformance of the required discovery methods (GAP + SDP + GATT).
- Aggregate the data into a more readable structure.


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

```
python bluetooth_scrapper/download_database_entries.py
```

```
python bluetooth_scrapper/download_device_details.py
```

Run the Python Notebook to see how to extract the raw data:
```
bluetooth_scrapper/data_analysis.py
```

## References
[1]: https://launchstudio.bluetooth.com/Listings/Search