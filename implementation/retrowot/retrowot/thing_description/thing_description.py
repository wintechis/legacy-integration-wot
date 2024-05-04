import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)
from rdflib import Graph, Literal
from rdflib.plugins.sparql import prepareQuery


from typing import Any, List
from configs import settings
from functools import lru_cache
from configs import logger
from thing_description.interaction_affordance import (
    PropertyAffordance,
    ActionAffordance,
    EventAffordance,
  
)
import aiohttp
import asyncio
import json
from fastapi.encoders import jsonable_encoder



SELECT_QUERY_SERVICE_TO_ACTION_AFFORDANCE = prepareQuery(
    """
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX prof: <http://www.w3.org/ns/dx/prof/>

SELECT ?affordanceId ?interactionType ?capabilityName ?protocolStack 
WHERE {
    ?device a capability:Device;
        capability:hasProtocolStack ?protocolStack;
        capability:hasAffordance ?affordance;
        capability:hasAddress ?deviceAddress.

    ?affordance # a ?affordanceType;
        capability:hasAffordanceID ?affordanceId;
        capability:hasInteraction ?interactionType.
        
    FILTER(?interactionType in (capability:ActionInteraction))
    
    BIND(?affordanceId as ?capabilityName)
      
}
"""
)


SELECT_QUERY_AFFORDANCE_COMMENT_ENRICHMENT = prepareQuery(
    """
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX prof: <http://www.w3.org/ns/dx/prof/>

SELECT ?comment 
WHERE {
    ?capability a capability:ServiceCapability;
        capability:hasProtocolStack ?protocolStack;
        capability:hasInteraction [
            capability:hasAffordanceID ?affordanceId;
            ];
        rdfs:comment ?comment.    
}
"""
)


SELECT_QUERY_SERVICE_TO_PROPERTY_AFFORDANCE = prepareQuery(
    """
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX prof: <http://www.w3.org/ns/dx/prof/>

SELECT ?affordanceId ?interactionType ?capabilityName ?protocolStack 
WHERE {
    ?device a capability:Device;
        capability:hasProtocolStack ?protocolStack;
        capability:hasAffordance ?affordance;
        capability:hasAddress ?deviceName.

    ?affordance # a ?affordanceType;
        capability:hasAffordanceID ?affordanceId;
        capability:hasInteraction ?interactionType.
        

        
    FILTER(?interactionType in (capability:ReadInteraction, capability:WriteInteraction))
    
    BIND(?affordanceId as ?capabilityName)

}
"""
)

SELECT_QUERY_SERVICE_TO_EVENT_AFFORDANCE = prepareQuery(
    """
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX prof: <http://www.w3.org/ns/dx/prof/>

SELECT ?affordanceId ?affordanceId2 ?interactionType ?capabilityName ?protocolStack 
WHERE {
    ?device a capability:Device;
        capability:hasProtocolStack ?protocolStack;
        capability:hasAffordance ?affordance;
        capability:hasAddress ?deviceName.

    ?affordance capability:hasAffordanceID ?affordanceId;
        capability:hasInteraction ?interactionType.
        
    FILTER(?interactionType = capability:SubscriptionCommand)
    BIND(?affordanceId as ?capabilityName)
}
"""
)

SELECT_QUERY_SERVICE_TO_ACTION_AFFORDANCE = prepareQuery(
    """
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX prof: <http://www.w3.org/ns/dx/prof/>

SELECT ?affordanceId ?interactionType ?capabilityName ?protocolStack 
WHERE {
    ?device a capability:Device;
        capability:hasProtocolStack ?protocolStack;
        capability:hasAffordance ?affordance;
        capability:hasAddress ?deviceAddress.

    ?affordance # a ?affordanceType;
        capability:hasAffordanceID ?affordanceId;
        capability:hasInteraction ?interactionType.
        
    FILTER(?interactionType in (capability:ActionInteraction))
    
    BIND(?affordanceId as ?capabilityName)
      
}
"""
)

SELECT_QUERY_GET_DEVICE_NAME = prepareQuery(
    """
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX td:  <https://www.w3.org/2019/wot/td#>

SELECT DISTINCT ?deviceName 
WHERE {
    ?device a capability:Device;
            td:title ?deviceName.
    }
"""
)

SELECT_QUERY_GET_DEVICE_NAME_2 = prepareQuery(
    """
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX prof: <http://www.w3.org/ns/dx/prof/>

SELECT DISTINCT ?deviceName 
WHERE {
    ?device a capability:Device;
            capability:hasAddress ?deviceName.
    }
"""
)

SELECT_QUERY_GET_DEVICE_ADDRESS = prepareQuery(
    """
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX prof: <http://www.w3.org/ns/dx/prof/>

SELECT DISTINCT ?deviceName 
WHERE {
    ?device a capability:Device;
            capability:hasAddress ?deviceName.
    }
"""
)

SELECT_QUERY_DEVICE_TYPES = prepareQuery(
    """
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX prof: <http://www.w3.org/ns/dx/prof/>

SELECT ?protocolStack 
WHERE {
    ?device a capability:Device;
        capability:hasProtocolStack ?protocolStack.
      
}
"""
)

class ThingDescription:
    def __init__(self, graph: Graph):
        if settings.enrichment.use_service_enrichment:
            graph = self._enrich_graph(graph)

        self.title: str = self._get_name(graph)
        self._device_address: str = self._get_address(graph)
        self.properties: List[PropertyAffordance] = self._get_property_affordances(
            graph
        )
        self.actions: List[ActionAffordance] = self._get_action_affordances(graph)
        self.events: List[EventAffordance] = self._get_event_affordances(graph)
        self.device_type = self._get_device_types(graph)
        logger.debug(
            f"Created ThingDescription for {self.title} with \
            {len(self.properties)} properties, {len(self.actions)} actions\
            and {len(self.events)} events"
        )

    async def publish_thing_description(self):
        """
        Publishes the thing description to the thing directory.

        Returns:
            A string representing the response from the thing directory.
        """
        
        async def _post(session, url, data):
            async with session.post(url, data=data) as response:
                return await response.text()
        
        file = jsonable_encoder(self.dict())
        

        async with aiohttp.ClientSession() as session:
            text = await _post(session=session, 
                    url=f"{settings.thing_directory.url}/{settings.thing_directory.post_endpoint}",
                    data=json.dumps(file))
            
            logger.debug(f"Response from thing directory: {text}")
            
            
    @lru_cache(maxsize=1)
    def _load_capability_graph(
        self, enrichment_file="./retrowot/servicecapability.ttl"
    ) -> Graph:
        logger.debug(f"Enrich graph with {enrichment_file}")
        return Graph().parse(source=enrichment_file, format="turtle")

    def _enrich_graph(self, graph: Graph) -> Graph:
        enrichments_graph = self._load_capability_graph()
        graph += enrichments_graph
        return graph

    def __str__(self) -> str:
        return str(self.dict())

    def _get_device_types(self, graph: Graph) -> str:
        res = ''
        device_type = [
            _.protocolStack.toPython()
            for _ in graph.query(SELECT_QUERY_DEVICE_TYPES)
        ]
        if len(device_type) > 0:
            res: str = device_type[0]
        return res
    
    def _get_address(self, graph: Graph) -> str:
        res = ''
        address = [
            _.deviceName.toPython()
            for _ in graph.query(SELECT_QUERY_GET_DEVICE_ADDRESS)
        ]
        if len(address) > 0:
            res: str = address[0]
        return res

    def _get_name(self, graph: Graph) -> str:
        
        res = ''
        deviceNames = [
            _.deviceName.toPython() for _ in graph.query(SELECT_QUERY_GET_DEVICE_NAME)
        ]

        if len(deviceNames) > 0:
            deviceNames = [
                _.deviceName.toPython()
                for _ in graph.query(SELECT_QUERY_GET_DEVICE_NAME_2)
            ]

            res = deviceNames[0]
        return res

    def _remove_duplicate_affordances(self, affordances):
        res_2 = {}
        for affordance in affordances:
            if affordance.title not in res_2:
                res_2[affordance.title] = affordance
            else:
                for form in affordance.forms:
                    exists: bool = False
                    for existing_form in res_2[affordance.title].forms:
                        if form == existing_form:
                            exists = True
                            break
                    if not exists:
                        res_2[affordance.title].forms += affordance.forms
                
        
        return list(res_2.values())
    
    def _get_property_affordances(self, graph: Graph) -> List[PropertyAffordance]:
        res = []
        graph.serialize("my_graph.ttl")
        for _ in graph.query(
            SELECT_QUERY_SERVICE_TO_PROPERTY_AFFORDANCE,
        #    initBindings={"deviceName": Literal(self._device_address)},
        ):
            
            affordance = PropertyAffordance(
                title=_.capabilityName.toPython(),
                interactionType=_.interactionType.toPython(),
                affordanceId=self._device_address + "/" + _.affordanceId.toPython(),
                graph=graph,
            )

            res.append(affordance)
            logger.debug(
                f"Added PropertyAffordance {affordance.title} with \
                 and affordanceId {_.affordanceId.toPython()} to ThingDescription"
            )
            
        # Check for duplicates and merge them
        res = self._remove_duplicate_affordances(res)
            
        return res

    def _get_action_affordances(self, graph: Graph) -> List[ActionAffordance]:
        res = []

        for _ in graph.query(
            SELECT_QUERY_SERVICE_TO_ACTION_AFFORDANCE,
            initBindings={"deviceName": Literal(self._device_address)},
        ):

            affordance = ActionAffordance(
                title=_.capabilityName.toPython(),
                interactionType=_.interactionType.toPython(),
                affordanceId=self._device_address + "/" + _.affordanceId.toPython(),
                graph=graph,
            )

            res.append(affordance)
            logger.debug(
                f"Added ActionAffordance {affordance.title} with \
                and affordanceId {_.affordanceId.toPython()} to ThingDescription"
            )
            
        # Check for duplicates and merge them
        res = self._remove_duplicate_affordances(res)
            
        return res

    def _get_event_affordances(self, graph: Graph) -> List[EventAffordance]:
        res = []
        for _ in graph.query(
            SELECT_QUERY_SERVICE_TO_EVENT_AFFORDANCE,
            initBindings={"deviceName": Literal(self._device_address)},
        ):
            affordance = EventAffordance(
                title=_.capabilityName.toPython(),
                interactionType=_.interactionType.toPython(),
                affordanceId=self._device_address + "/" + _.affordanceId.toPython(),
                graph=graph,
            )

            res.append(affordance)
            logger.debug(
                f"Added EventAffordance {affordance.title} with \
                and affordanceId {_.affordanceId.toPython()} to ThingDescription"
            )
                    
        # Check for duplicates and merge them
        res = self._remove_duplicate_affordances(res)
            
        return res

    def dict(self, *args, **kwargs):
        model_dict = {}
        model_dict["@context"] = ["https://www.w3.org/2019/wot/td/v1", "https://www.w3.org/2022/wot/td/v1.1"]
        
        if self.device_type == 'http://purl.org/serviceCapability#BluetoothLE':
            model_dict["@context"].append(
                {"sbo": "https://freumi.inrupt.net/SimpleBluetoothOntology.ttl#",
                "bdo": "https://freumi.inrupt.net/BinaryDataOntology.ttl#" }
            )
        model_dict["title"] = self.title
        model_dict["securityDefinitions"] = {"nosec_sc": {"scheme": "nosec"}}
        model_dict["security"] = ["nosec_sc"]
        
        

        model_dict["properties"] = {}
        model_dict["actions"] = {}
        model_dict["events"] = {}

        
        for _ in self.properties:
            model_dict["properties"][_._camel_case(_.title)] = _.dict()
        for _ in self.actions:
            model_dict["actions"][_._camel_case(_.title)] = _.dict()
        for _ in self.events:
            model_dict["events"][_._camel_case(_.title)] = _.dict()

        if self.properties == {}:
            del model_dict["properties"]
        if self.actions == {}:
            del model_dict["actions"]
        if self.events == {}:
            del model_dict["events"]
        return model_dict
    
    def to_tm(self):
        data = self.dict()
        data['base'] = "gatt://{{MacOrWebBluetoothId}}/"
        td_dump = json.dumps(data)
        td_dump = td_dump.replace(f"gatt://{self.title}/", "./")
        return td_dump

if __name__ == "__main__":
    from pyshacl import validate
    graph = Graph().parse("/home/rene/Repositories/PhD/retrowot/retrowot/zigbee_test_1_device.ttl", format="turtle")
    
    print("Length of graph: ", len(graph))
    
    shacl_graph = Graph().parse("../servicetranslation.ttl")

    print("Length of shacl graph: ", len(shacl_graph))
    validate(graph, shacl_graph=shacl_graph, advanced=True, inplace=True, debug=True)
    graph.serialize("enriched_test.ttl", format="turtle")
    print("Length of graph: ", len(graph))
 
    td = ThingDescription(graph=graph)
