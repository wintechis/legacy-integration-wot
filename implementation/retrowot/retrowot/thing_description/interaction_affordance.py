from pydantic import BaseModel
from typing import List, Union, Dict
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from thing_description.form import Form
import decimal
from functools import lru_cache
from rdflib.plugins.sparql import prepareQuery
from configs import settings

SELECT_QUERY_AFFORDANCE_COMMENT_ENRICHMENT = prepareQuery(
"""
PREFIX capability: <http://purl.org/serviceCapability#> 

SELECT ?description 
WHERE {
    ?capability a capability:ServiceCapability;
        capability:hasProtocolStack ?protocolStack;
        capability:hasInteraction [
            capability:hasAffordanceID ?affordanceId
            ];
        rdfs:comment ?description.    
}
"""
)
SELECT_QUERY_DEVICE_TYPE = prepareQuery(
"""
PREFIX capability: <http://purl.org/serviceCapability#> 

SELECT ?deviceType 
WHERE {
    ?device a capability:Device;
        capability:hasProtocolStack ?deviceType.

}
"""
)


SELECT_QUERY_AFFORDANCE_TITLE_ENRICHMENT = prepareQuery(
"""
PREFIX capability: <http://purl.org/serviceCapability#> 

SELECT ?capabilityName 
WHERE {
    ?capability a capability:ServiceCapability;
        capability:hasProtocolStack ?protocolStack;
        capability:hasInteraction [
            capability:hasAffordanceID ?affordanceId
            ];
        capability:represents ?capabilityName.    
}
"""
)

SELECT_QUERY_BYTELENGTH = prepareQuery(
"""
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX bdo: <https://freumi.inrupt.net/BinaryDataOntology.ttl#>
PREFIX dct: <http://purl.org/dc/terms/>
SELECT ?byteLength ?offset ?scalingFactor ?signed ?unit ?outputFormat
WHERE {
    ?capability a capability:ServiceCapability;
        capability:hasProtocolStack ?protocolStack;
        capability:hasInteraction [
            capability:hasAffordanceID ?affordanceId
            ];
        capability:hasDataModel ?dataModel.
        
        
        ?dataModel capability:hasDecodingRule ?decodingRule;
            capability:hasOutputFormat ?outputFormat.
            
        OPTIONAL {
            ?dataModel capability:hasUnit ?unit.
            }
            
        ?decodingRule dct:conformsTo bdo: .
        
        OPTIONAL {
            ?decodingRule bdo:bytelength ?byteLength.
        }
        OPTIONAL {
            ?decodingRule bdo:offset ?offset.
        }
        OPTIONAL {
            ?decodingRule bdo:scale ?scalingFactor.
        }
        
        OPTIONAL {
            ?decodingRule bdo:signed ?signed.
        }
}
"""
)


SELECT_QUERY_SERVICE_TO_INTERACTION_TYPES_FOR_PROPERTIES = prepareQuery(
    """
PREFIX capability: <http://purl.org/serviceCapability#> 
PREFIX prof: <http://www.w3.org/ns/dx/prof/>

SELECT DISTINCT ?interactionType
WHERE {

    ?affordance # a ?affordanceType;
        capability:hasAffordanceID ?affordanceId;
        capability:hasInteraction ?interactionType.
        

        
    FILTER(?interactionType in (capability:ReadInteraction, capability:WriteInteraction))
    
    BIND(?affordanceId as ?capabilityName)

}
"""
)

class InteractionAffordance:
    def __init__(
        self, title: str, interactionType: List[str], affordanceId: str, graph: Graph
    ):
        self.type: str = "string"
        self.title: str = self._get_title(title, graph)
        self._additional_fields: Dict = self._add_bytewise_interpretation(
            affordanceId, graph
        )
        self.forms: List[Form] = self._get_forms(
            interactionType, affordanceId, self.title, self._has_bytewise_interpretation(), graph
        )
        self.description: str = self._get_description(title, graph)
        # self.contentEncoding: str = "binary"
        # self.contentMediaType: str = "application/octet-stream"
        self._additional_fields: Dict = self._add_bytewise_interpretation(
            affordanceId, graph
        )
        
    # Write a function to create camel case from whitespace separated string
    def _camel_case(self, name: str) -> str:
        name = "".join(x.capitalize() for x in name.split(" "))
        return name
    
    @lru_cache(maxsize=128)
    def _get_query_result(self, query, name, value, graph, filter='first'):
        res = None
        if (name is None) or (value is None):
            query_result = [_ for _ in graph.query(query)]
        else:
            query_result = [_ for _ in graph.query(query, initBindings={name: value})]

        if filter == 'first':
            if len(query_result) > 0:
                res = query_result[0]
        elif filter == 'all':
            if len(query_result) > 0:
                res = query_result
            
        return res


    
    def _get_bytelength(self, title: str, graph: Graph) -> str:
        res = None
        bytelength = self._get_query_result(
            SELECT_QUERY_BYTELENGTH, "affordanceId", Literal(title), graph
        )

        if bytelength is not None:
            if bytelength.byteLength is not None:
                res = bytelength.byteLength.toPython()

        return res

    def _get_device_type(self, title: str, graph: Graph) -> str:
        title = title.replace("urn:uuid:", "")
        res = None
        device = self._get_query_result(
            SELECT_QUERY_DEVICE_TYPE, None, None, graph
        )

        if device is not None:
            if device.deviceType is not None:
                res = device.deviceType.toPython()



        #print(f"Affordance Id is: {title}, result of query is: {res}")
        return res
    
    def _get_signed(self, title: str, graph: Graph) -> str:
        res = None
        signed = self._get_query_result(
            SELECT_QUERY_BYTELENGTH, "affordanceId", Literal(title), graph
        )

        if signed is not None:
            if signed.signed is not None:
                res = signed.signed.toPython()

        return res



    def _get_unit(self, title: str, graph: Graph) -> str:
        res = None

        unit = self._get_query_result(
            SELECT_QUERY_BYTELENGTH, "affordanceId", Literal(title), graph
        )

        if unit:
            if unit.unit is not None:
                res = unit.unit.toPython()

        return res

    def _get_scale(self, title: str, graph: Graph) -> str:
        res = None

        scalingFactor = self._get_query_result(
            SELECT_QUERY_BYTELENGTH, "affordanceId", Literal(title), graph
        )

        if scalingFactor is not None:
            if scalingFactor.scalingFactor is not None:
                try:
                    res = decimal.Decimal(scalingFactor[0].scalingFactor.toPython())
                except:
                    res = None

        return res

    def _get_offset(self, title: str, graph: Graph) -> str:
        res = None
        offset = self._get_query_result(
            SELECT_QUERY_BYTELENGTH, "affordanceId", Literal(title), graph
        )

        if offset is not None:
            if offset.offset is not None:
                res = offset.offset.toPython()

        return res

    def _get_format(self, title: str, graph: Graph) -> str:
        res = "string"
        outputFormat = self._get_query_result(
            SELECT_QUERY_BYTELENGTH, "affordanceId", Literal(title), graph
        )

        if outputFormat is not None:
            if outputFormat.outputFormat is not None:
                outputFormat = outputFormat.outputFormat.toPython()
                print("My outputFormat is: ", outputFormat)
                match outputFormat:
                    case "https://www.w3.org/2019/wot/json-schema#NumberSchema":
                        res = "number"
                    case "https://www.w3.org/2019/wot/json-schema#IntegerSchema":
                        res = "integer"
                    case "https://www.w3.org/2019/wot/json-schema#BooleanSchema":
                        res = "boolean"
                    case "https://www.w3.org/2019/wot/json-schema#StringSchema":
                        res = "string"
                    case "https://www.w3.org/2019/wot/json-schema#ObjectSchema":
                        res = "object"
                    case "https://www.w3.org/2019/wot/json-schema#ArraySchema":
                        res = "array"
                    case "https://www.w3.org/2019/wot/json-schema#NullSchema":
                        res = "null"

        return res

    def _add_bytewise_interpretation(self, affordance_id: str, graph: Graph) -> Dict:
        """
        Use the BDO Ontology to add bytewise interpretation to the affordance.

        Args:
            affordance_id (str): The ID of the affordance.
            graph (Graph): The graph containing the BDO Ontology.

        Returns:
            dict: A dictionary containing the bytewise interpretation information.

        Example:
            Assume the graph contains for the affordance with the ID "urn:uuid:12345678" the following information:
            bdo:bytelength 4
            bdo:scale 1.0
            type integer
            bdo:signed False
            
            >>> affordance_id = "urn:uuid:12345678"
            >>> graph = Graph()
            >>> result = self._add_bytewise_interpretation(affordance_id, graph)
            >>> print(result)
            {'bdo:bytelength': 4, 'bdo:scale': 1.0, 'type': 'integer', 'bdo:signed': False}

        Raises:
            ValueError: If the affordance ID is invalid.
            GraphError: If there is an error accessing the BDO Ontology.

        Note:
            This method uses the BDO Ontology to determine the bytewise interpretation
            of the affordance. The resulting dictionary contains information such as
            byte length, scale, data type, signedness, and unit.

        """
        res = {}

        affordance_id = affordance_id.replace("urn:uuid:", "")
        affordance_id = "/".join(affordance_id.split("/")[1:])

        res["bdo:bytelength"] = self._get_bytelength(affordance_id, graph)
        res["bdo:scale"] = self._get_scale(affordance_id, graph)
        res["type"] = self._get_format(affordance_id, graph)
        res["bdo:signed"] = self._get_signed(affordance_id, graph)
        res["unit"] = self._get_unit(affordance_id, graph)

        # Remove None values
        res = {k: v for k, v in res.items() if v is not None}

        return res

    def _has_bytewise_interpretation(self) -> bool:
        """Check if the affordance has bytewise interpretation."""
        has_bytelength: bool = self._additional_fields.get("bdo:bytelength", None) is not None
        has_signing: bool =  self._additional_fields.get("bdo:signed", None) is not None
        has_scale: bool =  self._additional_fields.get("bdo:scale", None) is not None
   
        if has_bytelength or has_signing or has_scale:
            return True
        return False


    def __str__(self) -> str:
        return str(self.dict())

    def _get_description(self, title: str, graph: Graph) -> str:
        title = title.replace("urn:uuid:", "")
        description = self._get_query_result(
            SELECT_QUERY_AFFORDANCE_COMMENT_ENRICHMENT, "affordanceId", Literal(title), graph, 'all'
        )

        if description is not None:
            if isinstance(description, list):
                description = "".join([_.description.toPython() for _ in description])
            else:
                description = description.description.toPython()
            print(description)

        else:
            description = ""

        return description

    def _get_title(self, title: str, graph: Graph) -> str:
        title = title.replace("urn:uuid:", "")

        name = self._get_query_result(
            SELECT_QUERY_AFFORDANCE_TITLE_ENRICHMENT, "affordanceId", Literal(title), graph
        )

        if name is not None:
            name = name.capabilityName.toPython()
        else:
            name = title

        return name

    def _get_forms(
        self,
        interactionType,
        affordanceId,
        title,
        byte_wise_interpretation: bool,
        graph: Graph,
    ) -> List[Form]:
        res = []
        
        if settings.enrichment.middleware_interface:
            # Add the interaction via the server
            form = Form(
                href=affordanceId,
                op=interactionType,
                byte_wise_interpretation=byte_wise_interpretation,
                graph=graph,
                device_type=settings.server_type
            )
            
            res = [form]
        
        device_type = self._get_device_type(title, graph)
        if settings.enrichment.use_primary_interface:
            # Add the direct interaction with the device
            additional_form = Form(
                href=affordanceId,
                op=interactionType,
                byte_wise_interpretation=byte_wise_interpretation,
                graph=graph,
                device_type=device_type
            )
            
            res.append(additional_form)
        return res

    def dict(self, *args, **kwargs):
        model_dict = {
            "type": self.type,
            "title": self._camel_case(self.title),
            "forms": [_.dict() for _ in self.forms],
   #         "contentEncoding": self.contentEncoding,
   #         "contentMediaType": self.contentMediaType,
        }

        if self.description != "":
            model_dict["description"] = self.description

        if self._additional_fields != {}:
            model_dict.update(self._additional_fields)

        return model_dict


class PropertyAffordance(InteractionAffordance):
    def __init__(
        self, title: str, interactionType: str, affordanceId: str, graph: Graph
    ):
        #interactionTypes = self._get_interaction_types(affordanceId, graph)
        super().__init__(title, interactionType, affordanceId, graph)
        self.observable: Union[bool, None] = None
        self.readOnly: Union[bool, None] = None
        self.writeOnly: Union[bool, None] = None

    def _get_interaction_types(self, affordanceId: str, graph: Graph) -> List[str]:
        res = []
        for _ in graph.query(
            SELECT_QUERY_SERVICE_TO_INTERACTION_TYPES_FOR_PROPERTIES,
            initBindings={"affordanceId": URIRef(affordanceId)},
        ):
            res.append(_.interactionType.toPython())
            
            
        return res
    
    
    
    def __str__(self) -> str:
        return str(self.dict())

    def dict(self, *args, **kwargs):
        model_dict = super().dict()

        if self.observable != None:
            model_dict["observable"] = self.observable
        if self.readOnly != None:
            model_dict["readOnly"] = self.readOnly
        if self.writeOnly != None:
            model_dict["writeOnly"] = self.writeOnly
        return model_dict


class ActionAffordance(InteractionAffordance):
    def __init__(
        self, title: str, interactionType: str, affordanceId: str, graph: Graph
    ):
        super().__init__(title, interactionType, affordanceId, graph)
        self.safe: Union[bool, None] = None
        self.idempotent: Union[bool, None] = None

    def __str__(self) -> str:
        return str(self.dict())

    def dict(self, *args, **kwargs):
        model_dict = super().dict()

        if self.safe != None:
            model_dict["safe"] = self.safe
        if self.idempotent != None:
            model_dict["idempotent"] = self.idempotent
        return model_dict


class EventAffordance(InteractionAffordance):
    def __init__(
        self, title: str, interactionType: str, affordanceId: str, graph: Graph
    ):
        super().__init__(title, interactionType, affordanceId, graph)
        self.cancellation_link: str = ""
        self.subscription_link: str = ""
        

    def dict(self, *args, **kwargs):
        model_dict = super().dict()
        
        if self.cancellation_link != "":
            model_dict["cancellation"] = self.cancellation_link
            
        model_dict["data"] = {
            "type": model_dict.pop("type"),
        }
        

        if  "bdo:bytelength" in model_dict:
            model_dict["data"]["bdo:bytelength"] = model_dict.pop("bdo:bytelength")

        if "bdo:signed" in model_dict :
            model_dict["data"]["bdo:signed"] = model_dict.pop("bdo:signed")
        
        if  "bdo:scale" in model_dict:
            model_dict["data"]["bdo:scale"] = model_dict.pop("bdo:scale")
            
        return model_dict
        
        

            
    def __str__(self) -> str:
        return str(self.dict())
