| |**Ontology Requirements Specification Document The Simple Service Capability Ontology (SCO)**  |
|--------|-----------------------------------------------------------------------------------|
| **1**  | **Purpose**                             |
|        | The purpose of this ontology is to provide a lightweight representation of service capabilities from devices using different IoT protocol stacks such as Bluetooth, Zigbee, CoAP, Matter, that can be used by software agents to translate service descriptions of devices into functional TDs.       |
| **2**  | **Scope**    |
|        | The current scope of SCO is focused as a semantic model to translate devices from a variety of IoT protocol stack to TDs. It focuses on three main components necessary to represent any device. Its addressing information, the capability definition and the interaction methods.  <ul> <li> **Service Capabilities:** . This part of the model represents the content of a service capability. </li> <li> **Service Interaction**  This part of the ontology focuses on service capabilites, sometimes called Characteristics (Bluetooth), Endpoints (Zigbee, OPC UA, Matter) or affordances, how to address them, and there semantic access mode. </li> <li> **Identification of Device:**  This includes any device addressing information to uniquely identify a device. </li> </ul> |
| **3**  | **Implementation Language (optional)**                                                                         |
|        | RDFS Ontology Language                                                       |
| **4**  | **Intended End-Users (optional)**                                                                              |
|        | <ul>  <li> IoT Developer </li><li> WoT Developer <li>Smart Gateways (e.g. WoT Intermediaries) </li> <li>Software Agents</li> </li> </ul>                                        |
| **5**  | **Intended Uses**                       |
|        | <ul> <li> Allows the description of interpretations of en- and decodings. </li> <li> Generation of semantic interface descriptions (e.g. Thing Descriptions) </li> <li> Knowledge Graph Construction </li> </ul> (for specific use cases please see  [SCO Use Case Specification Document](../usecases/use-case-specification.md)                                       |
| **6**  | **Ontology Requirements**               |
|        | **Non-Functional Requirements**         |
|        | <ul> <li>Reuse of existing ontologies to describe de- and encoding functions </li> <li> Reusability of the ontology </li> <li> Standardization and semantic interoperability </li> <li> Online availability </li> <li> Must be able to be translated into terms of the WoT Thing description </li> <li> Resources must be labeled and commented in English. </li> </ul>                                                            |
|        | **Functional Requirements: Lists or tables of (domain) requirements written as Competency Questions and sentences**                                                                   |
|        | See [SCO's requirements](./domain-requirements-table.xlsx)                      |

