from pydantic import BaseModel
from typing import List, Any
from zigbee.datamodel import Endpoint, Cluster

from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef

ZIG = Namespace("https://www.purl.org/SimpleZigbeeInteractionOntology.ttl#")
UUID = Namespace("urn:uuid:")
ME = Namespace("https://127.0.0.1/Me.ttl#")

class ZigbeeDevice(BaseModel):
    ieee: str
    nwk: int
    manufacturer: str
    manufacturer_id: int
    model: str
    endpoints: List[Endpoint]
    thing_description: Any = None   
 
    
    def is_discovered(self) -> bool:
        return True
    
    def to_rdf(self):
        g = Graph()
        device_hash = str(abs(hash(self.ieee)))
        DEVICE_URI = URIRef(value=device_hash, base=ME)
        g.add((DEVICE_URI, RDF.type, ZIG.EndNode))
        g.add((DEVICE_URI, ZIG.hasIEEEAddress, Literal(self.ieee)))
        g.add((DEVICE_URI, ZIG.hasNWKAddress, Literal(self.nwk)))
        g.add((DEVICE_URI, ZIG.hasManufacturer, Literal(self.manufacturer)))
        g.add((DEVICE_URI, ZIG.hasManufacturerID, Literal(self.manufacturer_id)))
        g.add((DEVICE_URI, ZIG.hasDeviceModel, Literal(self.model)))
        
        for endpoint in self.endpoints:
            g = endpoint.to_rdf(g, DEVICE_URI, device_hash)
        
        return g