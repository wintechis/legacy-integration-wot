from enum import Enum
from typing import Any

from pydantic import BaseModel
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from utils import normalize_bluetooth_uuid

SBO = Namespace("https://freumi.inrupt.net/SimpleBluetoothOntology.ttl#")
SBOE = Namespace("https://purl.org/ExtendedSimpleBluetoothOntology#")
ME = Namespace("https://127.0.0.1/Me.ttl#")


class AddressType(Enum):
    PUBLIC = "PUBLIC"
    RANDOM = "RANDOM"
    PUBLIC_ID = "PUBLIC_ID"
    RANDOM_ID = "RANDOM_ID"


class AccessMethod(Enum):
    READ = "READ"
    WRITE = "WRITE"
    NOTIFY = "NOTIFY"
    INDICATE = "INDICATE"
    WRITE_WITHOUT_RESPONSE = "WRITE_WITHOUT_RESPONSE"


class Descriptor(BaseModel):
    uuid: Any
    handle: int
    value: bytes

    def to_rdf(
        self, graph: Graph, characteristic_uri: URIRef, characteristic_hash
    ) -> Graph:
        descriptor_hash = str(abs(hash(self.uuid + characteristic_hash)))
        DESCRIPTOR_URI = URIRef(value=descriptor_hash, base=ME)
        uuid = normalize_bluetooth_uuid(self.uuid)
        graph.add((DESCRIPTOR_URI, RDF.type, SBO.Descriptor))
        graph.add((characteristic_uri, SBO.hasDescriptor, DESCRIPTOR_URI))
        graph.add((DESCRIPTOR_URI, SBO.hasUUID, Literal(uuid)))
        graph.add((DESCRIPTOR_URI, SBOE.hasHandle, Literal(self.handle)))
        graph.add((DESCRIPTOR_URI, SBOE.hasValue, Literal(self.value)))
        return graph


class Characteristic(BaseModel):
    uuid: str
    descriptors: list[Descriptor]
    properties: list[str]
    handle: int

    def to_rdf(self, graph: Graph, service_uri: URIRef, service_hash: str) -> Graph:
        characteristic_hash = str(abs(hash(self.uuid + service_hash)))
        CHARACTERISTIC_URI = URIRef(value=characteristic_hash, base=ME)
        uuid = normalize_bluetooth_uuid(self.uuid)

        graph.add((CHARACTERISTIC_URI, RDF.type, SBO.Characteristic))
        graph.add((service_uri, SBO.hasCharacteristic, CHARACTERISTIC_URI))
        graph.add((CHARACTERISTIC_URI, SBO.hasUUID, Literal(uuid)))
        graph.add((CHARACTERISTIC_URI, SBOE.hasHandle, Literal(self.handle)))

        # print(uuid, self.properties)

        for property in self.properties:
            # print(property)
            if property == "NOTIFY":
                graph.add((CHARACTERISTIC_URI, SBO.methodName, SBO.notify))
            elif property == "READ":
                graph.add((CHARACTERISTIC_URI, SBO.methodName, SBO.read))
            elif property == "WRITE":
                graph.add((CHARACTERISTIC_URI, SBO.methodName, SBO.write))
            elif property == "WRITE_WITHOUT_RESPONSE":
                graph.add(
                    (
                        CHARACTERISTIC_URI,
                        SBO.methodName,
                        URIRef(SBO + "write-without-response"),
                    )
                )
            elif property == "INDICATE":
                graph.add((CHARACTERISTIC_URI, SBO.methodName, SBOE.indicate))
            elif property == "AUTHENTICATED_SIGNED_WRITES":
                graph.add(
                    (
                        CHARACTERISTIC_URI,
                        SBO.methodName,
                        URIRef(value="authenticated-signed-writes", base=SBOE),
                    )
                )
            elif property == "EXTENDED_PROPERTIES":
                graph.add(
                    (
                        CHARACTERISTIC_URI,
                        SBO.methodName,
                        URIRef(value="extended-properties", base=SBOE),
                    )
                )
            elif property == "BROADCAST":
                graph.add((CHARACTERISTIC_URI, SBO.methodName, SBOE.broadcast))

        for descriptor in self.descriptors:
            graph = descriptor.to_rdf(graph, CHARACTERISTIC_URI, characteristic_hash)
        return graph


class Service(BaseModel):
    uuid: str
    characteristics: list[Characteristic]

    def to_rdf(self, graph: Graph, device_uri: URIRef, device_hash) -> Graph:
        service_hash = str(abs(hash(self.uuid + device_hash)))
        SERVICE_URI = URIRef(value=str(self.uuid), base=ME)
        uuid = normalize_bluetooth_uuid(self.uuid)
        graph.add((SERVICE_URI, RDF.type, SBO.Service))
        graph.add((device_uri, SBO.hasService, SERVICE_URI))
        graph.add((SERVICE_URI, SBO.hasUUID, Literal(uuid)))

        for characteristic in self.characteristics:
            graph = characteristic.to_rdf(graph, SERVICE_URI, service_hash)

        return graph
