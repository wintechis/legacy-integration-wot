from pydantic import BaseModel
from enum import Enum
import datetime
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from typing import Any, List, Callable
from bluetooth.datamodel import Service, Characteristic, Descriptor

SBO = Namespace("https://freumi.inrupt.net/SimpleBluetoothOntology.ttl#")
SBOE = Namespace("https://purl.org/ExtendedSimpleBluetoothOntology#")
ME = Namespace("https://127.0.0.1/Me.ttl#")
UUID = Namespace("urn:uuid:")
    
class AddressType(Enum):
    PUBLIC = 'PUBLIC'
    RANDOM = 'RANDOM'
    PUBLIC_ID = 'PUBLIC_ID'
    RANDOM_ID = 'RANDOM_ID'
    
  
class Address(BaseModel):
    uuid: str
    address_type: AddressType
    static: bool
    resolvable: bool
    irk: str = ''
    
    def to_rdf(self, g: Graph, device_uri: URIRef) -> Graph:
        address_hash = str(abs(hash(self.uuid)))
        ADDRESS_URI = URIRef(value=address_hash, base=ME)
        g.add((ADDRESS_URI, RDF.type, SBOE.BluetoothAddress))
        g.add((ADDRESS_URI, RDF.type, URIRef(self.address_type.value, base=SBOE))) 
        g.add((ADDRESS_URI, SBOE.isStatic, Literal(self.static)))
        g.add((ADDRESS_URI, SBOE.isResolvable, Literal(self.resolvable)))
        g.add((ADDRESS_URI, SBOE.hasIRK, Literal(self.irk)))   
        g.add((ADDRESS_URI, SBOE.hasMacAddress, Literal(str(self.uuid)))) 
        g.add((device_uri, SBOE.hasAddress, ADDRESS_URI))
        return g
    
class BLEDeviceMessage(BaseModel):
    device: 'BLEDevice'
    timestamp: datetime.datetime = datetime.datetime.now()
    manufacturer_data: bytes = b''
    advertisement_data: str = ''
    rssi: int = 0
    
    
class DeviceInformation(BaseModel):
    information: Any
    predicate: URIRef
    
    class Config:
        arbitrary_types_allowed=True
    
    def to_rdf(self, g: Graph, device_uri: URIRef) -> Graph:
        if self.information is not None:
            g.add((device_uri, self.predicate, Literal(str(self.information))))
        return g
    
    
class BLEDevice(BaseModel):
    name: str
    manufacturer_specific_data: bytes
    manufacturer: str
    address: Address
    rssi: int
    data: str
    connectable: bool
    scannable: bool
    anonymous: bool
    legacy: bool
    complete: bool
    truncated: bool
    primary_phy: int
    secondary_phy: int
    services: list[Service] = []
    thing_description: Any = None
    messages: List[BLEDeviceMessage] = []
    discovered_device_information: List[DeviceInformation] = []
        
    def is_discovered(self) -> bool:
        return len(self.services) > 0
    
    def is_connectable(self) -> bool:
        return self.connectable
    
    
    def to_rdf(self):
        g = Graph("Oxigraph")
        device_hash = str(abs(hash(str(self.address.uuid) + "device")))
        DEVICE_URI = URIRef(value=device_hash,base=ME)
        g.add((DEVICE_URI, RDF.type, SBO.BluetoothLEDevice))
        
        # Check if the device is connectable
        if self.connectable:
            # It is a peripheral
            g.add((DEVICE_URI, SBO.hasGAPRole, SBO.Peripheral))
            g.add((DEVICE_URI, SBO.isConnectable, Literal(True)))
        else:
            # It is a broadcaster
            g.add((DEVICE_URI, SBO.hasGAPRole, SBO.Broadcaster))
            g.add((DEVICE_URI, SBO.isConnectable, Literal(False)))
        
        g.add((DEVICE_URI, SBOE.hasName, Literal(self.name)))    
        g.add((DEVICE_URI, SBOE.hasManufacturer, Literal(self.manufacturer)))
        g.add((DEVICE_URI, SBOE.hasManufacturerSpecificData, Literal(self.manufacturer_specific_data)))
        
        # Get the address type
        g = self.address.to_rdf(g, DEVICE_URI)
        
        
        for service in self.services:
            g = service.to_rdf(g, DEVICE_URI, device_hash)
            
        # Add additional metainformation
        for information in self.discovered_device_information:
            g = information.to_rdf(g, DEVICE_URI)
    
        
        # g.serialize(destination='test.ttl', format='turtle')
        return g
    

    
    
