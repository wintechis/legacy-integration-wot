from typing import List, Any
from pydantic import BaseModel
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from pydantic import Field




ZIG = Namespace("https://www.purl.org/SimpleZigbeeInteractionOntology.ttl#")
UUID = Namespace("urn:uuid:")
ME = Namespace("https://127.0.0.1/Me.ttl#")

class Command(BaseModel):
    name: str
    id: int
    properties: List[str]
    type: Any
    
    def to_rdf(self,  graph: Graph, cluster_node: URIRef, cluster_hash) -> Graph:
        command_hash = str(abs(hash(str(self.id) + cluster_hash)))
        COMMAND_URI = URIRef(value=command_hash, base=ME)
        
        graph.add((COMMAND_URI, RDF.type, ZIG.Command)) 
        graph.add((cluster_node, ZIG.hasCommand, COMMAND_URI))  
        graph.add((COMMAND_URI, ZIG.hasUUID, Literal(f"{self.id:04x}")))
        
        for property in self.properties:
            if property == "READ":
                graph.add((COMMAND_URI, ZIG.methodName, ZIG.Read))
            elif property == "WRITE":
                graph.add((COMMAND_URI, ZIG.methodName, ZIG.Write))
            elif property == "REPORT":
                graph.add((COMMAND_URI, ZIG.methodName, ZIG.Report))
            elif property == "WRITE_OPTIONAL":
                graph.add((COMMAND_URI, ZIG.methodName, ZIG.WriteOptional)) 
        
        
        
        return graph


class ClientCommand(Command):
    
    def to_rdf(self, graph: Graph, cluster_node: URIRef, cluster_hash) -> Graph:
        graph = super().to_rdf(graph, cluster_node, cluster_hash)
        command_hash = str(abs(hash(str(self.id) + cluster_hash)))
        COMMAND_URI = URIRef(value=command_hash, base=ME)
        graph.add((COMMAND_URI, RDF.type, ZIG.ClientCommand))
        return graph   


class ServerCommand(Command):
    
    def to_rdf(self, graph: Graph, cluster_node: URIRef, cluster_hash) -> Graph:
        graph = super().to_rdf(graph, cluster_node, cluster_hash)
        command_hash = str(abs(hash(str(self.id) + cluster_hash)))
        COMMAND_URI = URIRef(value=command_hash, base=ME)
        graph.add((COMMAND_URI, RDF.type, ZIG.ClientCommand))
        return graph   



class Attribute(BaseModel):
    name: str
    id: int
    properties: List[Any]
    type: Any
    
    def to_rdf(self,  graph: Graph, cluster_node: URIRef, cluster_hash) -> Graph:
        attribute_hash = str(abs(hash(str(self.id) + cluster_hash)))
        ATTRIBUTE_URI = URIRef(value=attribute_hash, base=ME)
        
        graph.add((ATTRIBUTE_URI, RDF.type, ZIG.Attribute)) 
        graph.add((cluster_node, ZIG.hasAttribute, ATTRIBUTE_URI))  
        graph.add((ATTRIBUTE_URI, ZIG.hasUUID, Literal(f"{self.id:04x}")))
        
        for property in self.properties:
            if property == "READ":
                graph.add((ATTRIBUTE_URI, ZIG.methodName, ZIG.Read))
            elif property == "WRITE":
                graph.add((ATTRIBUTE_URI, ZIG.methodName, ZIG.Write))
            elif property == "REPORT":
                graph.add((ATTRIBUTE_URI, ZIG.methodName, ZIG.Report))
            elif property == "WRITE_OPTIONAL":
                graph.add((ATTRIBUTE_URI, ZIG.methodName, ZIG.WriteOptional)) 
        
        
        
        return graph

class Cluster(BaseModel):
    name: str
    cluster_id: int
    attributes: List[Attribute]
    commands: List[Command]
    zigpy_cluster: Any = Field(exclude=True)
    
  

    def to_rdf(self,  graph: Graph, endpoint_uri: URIRef, endpoint_hash) -> Graph:
        attribute_hash = str(abs(hash(str(self.cluster_id) + endpoint_hash)))
        CLUSTER_URI = URIRef(value=attribute_hash, base=ME) 
        graph.add((CLUSTER_URI, RDF.type, ZIG.Cluster)) 
        graph.add((endpoint_uri, ZIG.hasCluster, CLUSTER_URI))  
        graph.add((CLUSTER_URI, ZIG.hasUUID, Literal(f"{self.cluster_id:04x}"))) 
        for attribute in self.attributes:
            graph = attribute.to_rdf(graph, CLUSTER_URI, attribute_hash)
        for command in self.commands:
            graph = command.to_rdf(graph, CLUSTER_URI, attribute_hash)
        return graph
    
    
class InCluster(Cluster):
    
    def to_rdf(self,  graph: Graph, endpoint_uri: URIRef, endpoint_hash) -> Graph:
        graph = super().to_rdf(graph, endpoint_uri, endpoint_hash)
        
        attribute_hash = str(abs(hash(str(self.cluster_id) + endpoint_hash)))
        CLUSTER_URI = URIRef(value=attribute_hash, base=ME) 
        graph.add((CLUSTER_URI, RDF.type, ZIG.InCluster))
        
        return graph 
    
class OutCluster(Cluster):
    
    def to_rdf(self,  graph: Graph, endpoint_uri: URIRef, endpoint_hash) -> Graph:
        graph = super().to_rdf(graph, endpoint_uri, endpoint_hash)
        
        attribute_hash = str(abs(hash(str(self.cluster_id) + endpoint_hash)))
        CLUSTER_URI = URIRef(value=attribute_hash, base=ME) 
        graph.add((CLUSTER_URI, RDF.type, ZIG.OutCluster))
        
        return graph 
    
class Endpoint(BaseModel):
    name: int
    clusters: List[Cluster]
    

    def to_rdf(self,  graph: Graph, device_uri: URIRef, device_hash) -> Graph:
        endpoint_hash = str(abs(hash(str(self.name) + device_hash)))
        ENDPOINT_URI = URIRef(value=endpoint_hash, base=ME) 
        graph.add((ENDPOINT_URI, RDF.type, ZIG.Endpoint)) 
        graph.add((device_uri, ZIG.hasEndpoint, ENDPOINT_URI))  
        graph.add((ENDPOINT_URI, ZIG.hasUUID, Literal(f"{self.name:04x}"))) 

        for cluster in self.clusters:   
            graph = cluster.to_rdf(graph, ENDPOINT_URI, endpoint_hash)
            
        return graph