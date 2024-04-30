# Data Scrapper for ZigBee 
This script contains the different components to extract bluetooth device information from the Bluetooth Listing Database. 

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
python zigbee_scrapper/download_database_entries.py
```

```
python zigbee_scrapper/download_device_details.py
```

```
zigbee_scrapper/extract_device_details.py
```


Run the Python Notebook to see how to extract the raw data: