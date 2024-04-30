# Use Case Specification of the Service Capability Ontology

The following document introduces example use cases for the Service Capability Ontology. The use case specification is aligned with the standards of the Linked Open Terms Methodology.



## Use Case 1: Enhancing Home Automation Systems with Legacy Device Integration

### Description:
A homeowner wants to include IoT, legacy home appliances (like Bluetooth, Zigbee, Matter) in their existing home automation system to enhance functionality, such as scheduling and remote control, without replacing the appliances.
For instance, a Bluetooth scale should be included in the Smart Home such that a homeowner can directly access the time series data of his weight over a dashboard and make predictions of his future weight.
This integration requires identifying the appliances, understanding their capabilities, and establishing communication with the home automation system.

### Actors:
- Legacy home appliances
- home automation system.

### Flow:
The process starts with the use of identification and discovery mechanisms to recognize each legacy appliance and outline its capabilities via the SCO ontology.
These capabilities are then translated into Thing Descriptions.
As a result, the home automation system can seamlessly communicate with the legacy appliances, enabling scheduled operations and remote control functionalities, thus expanding the system's capabilities without significant investment in new appliances.

## Use Case 2: Retrofitting Legacy Manufacturing Equipment into a Smart Factory System

### Description:
A manufacturing company seeks to integrate its equipment, which lacks WoT TDs, into its newly adopted smart factory system.
The system than allows seamless monitoring of equipment status and production processes of devices described with a WoT TD. 
For instance, the vibration and temperature of a production line are monitored to see the status of the production line.
The integration requires identifying each piece of legacy equipment, understanding its capabilities, and facilitating communication with the smart factory's management software without necessitating hardware modifications.

### Realworld Example:
- [AI-Naylze-Project](https://www.scs.fraunhofer.de/de/referenzen/ai-nalyze.html): A research project between Fraunhofer, Siemens, and Trevisto to improve transparency of production lines.

### Actors:
- Legacy equipment
- Smart factory management software.

### Flow:
The integration process begins with the identification of the legacy equipment using network-specific protocols.
Next, the capabilities of each piece of equipment are discovered and described using the SCO ontology, focusing on the equipment's identification, capabilities, and interaction methods with the smart factory network.
These capabilities are then mapped onto Thing Descriptions (TDs) using SPARQL queries, enhanced with additional information from the discovery process.
This enables the smart factory management software to interact with the legacy equipment, treating it as part of the IoT ecosystem.

## Use Case 3: Remote Monitoring and Control of Agricultural Equipment

### Description:
A farm wishes to remotely monitor and control its agricultural equipment, including legacy irrigation systems, to optimize water usage based on soil moisture levels and weather forecasts.
The farm has multiple fields and greenhouses. On the fields water flow and soil moisture data is collected with a protocol such as OMS over mioty and in the greenhouses with Zigbee sensors.  
This requires integrating the complete irrigation systems into an IoT-based monitoring and control platform, allowing for real-time data collection and automated decision-making.

### Realworld Example:
- [Greenhouse Wireless Monitoring System Based on ZigBee](https://link.springer.com/chapter/10.1007/978-3-642-36124-1_14): A research project between Fraunhofer, Siemens, and Trevisto to improve transparency of production lines.
- [Water Consumption Measurement with Mioty Diehl](https://www.diehl.com/metering/en/customer-cases/iot-smart-meters-for-a-sustainable-water-consumption/): 

### Actors:
- Agricultural equipment
- IoT-based monitoring and control platform.

### Flow:
Each piece of agricultural equipment is identified and its capabilities are discovered using protocols supported by the SCO ontology.
The equipment's interaction capabilities and data exchange formats are then described using the SCO model, aligning them with the IoT platform's requirements.
This description allows the platform to generate Thing Descriptions for each piece of equipment, enabling automated control strategies based on real-time data and external inputs like weather forecasts.


## Use Case 4: Environmental Monitoring with Legacy Sensors

### Description:
An environmental monitoring system seeks to incorporate legacy sensors that monitor various parameters (e.g., temperature, humidity, air quality) but do not support direct internet connectivity or modern IoT protocols.

### Actors:
- Legacy environmental sensors,
- data aggregator (WoT gateway),
- environmental monitoring application.

### Flow:
The data aggregator uses the "XYZ" method to discover the sensors and understand their capabilities through protocols like CoAP or Zigbee.
Using the SCO ontology, it models the sensors’ TDs, incorporating their unique identifiers, capabilities, and interaction methods.
 The environmental monitoring application can query and aggregate data from these sensors, enabling comprehensive monitoring without replacing the legacy equipment.

