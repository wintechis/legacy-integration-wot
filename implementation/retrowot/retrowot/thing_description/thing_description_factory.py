import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)
from typing import Callable, Dict, Optional

from configs import logger, settings
from pydantic import BaseModel, Field
from rdflib import Graph, URIRef
from thing_description.models import (
    InteractionAffordance,
    InteractionAffordanceType,
    ThingDescription,
)
from thing_description.ontology_alignment import Alignment
from thing_description.queries import (
    baseUri_and_title_query,
    interaction_affordance_query,
    thing_description_discovery_query,
    thing_model_discovery_query,
)
from thing_description.utils import query_result_to_dict


class ThingModelInstance(BaseModel):
    tm: str = Field(description="The thing model")
    interactionAffordance: str = Field(
        description="The property affordance of the thing"
    )
    interactionAffordanceForm: str = Field(description="The property affordance form")
    target: str = Field(description="The target of the affordance")
    affordanceType: str = Field(description="The affordance type")

    def __init__(self, **data):
        super().__init__(**data)

        affordanceType = self.affordanceType.split("#")[-1]
        if affordanceType == "PropertyAffordance":
            self.affordanceType = InteractionAffordanceType.PROPERTY_AFFORDANCE
        elif affordanceType == "ActionAffordance":
            self.affordanceType = InteractionAffordanceType.ACTION_AFFORDANCE
        elif affordanceType == "EventAffordance":
            self.affordanceType = InteractionAffordanceType.EVENT_AFFORDANCE


class ThingModelDiscoveryResult(BaseModel):
    baseUri: Optional[str] = Field(None, description="The base URI of the thing")
    interactionAffordanceUri: str = Field(
        None,
        alias="interactionAffordance",
        description="The property affordance of the thing",
    )
    interactionAffordanceFormUri: Optional[str] = Field(
        None,
        alias="interactionAffordanceForm",
        description="The property affordance form",
    )
    target: Optional[str] = Field(None, description="The target of the affordance")

    affordanceType: Optional[str] = Field(None, description="The affordance type")

    def __init__(self, **data):
        super().__init__(**data)

        if self.affordanceType is not None:
            affordanceType = self.affordanceType.split("#")[-1]
            if affordanceType == "PropertyAffordance":
                self.affordanceType = InteractionAffordanceType.PROPERTY_AFFORDANCE
            elif affordanceType == "ActionAffordance":
                self.affordanceType = InteractionAffordanceType.ACTION_AFFORDANCE
            elif affordanceType == "EventAffordance":
                self.affordanceType = InteractionAffordanceType.EVENT_AFFORDANCE


def get_thing_model_thing_description_matching(alignment_type: Alignment) -> Callable:
    def bluetooth_gatt_matching(
        discovery_result: ThingModelDiscoveryResult, thing_models: Graph
    ):
        query = """
        PREFIX hctl: <https://www.w3.org/2019/wot/hypermedia#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX tm:  <https://www.w3.org/2019/wot/tm#>
        PREFIX td:  <https://www.w3.org/2019/wot/td#> 

        SELECT ?thingModel
        WHERE {
            ?thingModel a tm:ThingModel;
            ?aTR [
                    td:hasForm [
                        hctl:hasTarget ?tm_target
                ]
            ].
            FILTER(?aTR in (td:hasActionAffordance, td:hasPropertyAffordance, td:hasEventAffordance))
            FILTER(STRENDS(LCASE(STR(?thingdescription_href)), LCASE(STR(?tm_target))))
            }
        LIMIT 1
        """
        query = query.replace(
            "?thingdescription_href", '"' + discovery_result.target + '"'
        )

        query_result = thing_models.query(query)
        result = query_result_to_dict(query_result)

        res = None
        try:
            res = result[0]["thingModel"]
        except Exception:
            pass
        return res

    def zigbee_matching(
        discovery_result: ThingModelDiscoveryResult, thing_models: Graph
    ):
        query = """
        PREFIX hctl: <https://www.w3.org/2019/wot/hypermedia#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX tm:  <https://www.w3.org/2019/wot/tm#>
        PREFIX td:  <https://www.w3.org/2019/wot/td#> 

        SELECT ?thingModel
        WHERE {
                ?thingModel a tm:ThingModel;
                    ?aTR [
                        td:hasForm [
                            hctl:hasTarget ?tm_target
                        ]
                    ].
                FILTER(?aTR in (td:hasActionAffordance, td:hasPropertyAffordance, td:hasEventAffordance))
                FILTER(STRENDS(LCASE(?thingdescription_href),  LCASE(STR(?tm_target))))
            }
        LIMIT 1
        """

        query = query.replace(
            "?thingdescription_href", '"' + discovery_result.target + '"'
        )

        query_result = thing_models.query(query)
        result = query_result_to_dict(query_result)

        res = None
        try:
            res = result[0]["thingModel"]
        except IndexError:
            pass
        return res

    if alignment_type.value == Alignment.Bluetooth_GATT.value:
        logger.debug("Bluetooth GATT alignment")
        return bluetooth_gatt_matching
    if alignment_type.value == Alignment.ZIGBEE.value:
        logger.debug("Zigbee alignment")
        return zigbee_matching


class ThingFactory:
    thing_models_graph: Graph
    background_knowledge_graph: Graph

    def __init__(self, thing_models_graph: Graph):
        self.thing_models_graph = thing_models_graph
        td_ontology = Graph(store="Oxigraph").parse(
            settings.ontologies.thing_description_ontology_path, format="ttl"
        )
        tm_ontology = Graph(store="Oxigraph").parse(
            settings.ontologies.thing_model_ontology_path, format="ttl"
        )
        hctl_ontology = Graph(store="Oxigraph").parse(
            settings.ontologies.hypermedia_ontology_path, format="ttl"
        )
        self.background_knowledge_graph = td_ontology + tm_ontology + hctl_ontology
        self._thing_models: Dict[str, ThingModelInstance] = self.get_thing_models(
            thing_models_graph + td_ontology + hctl_ontology + tm_ontology
        )

    def get_thing_models(
        self, thing_models_graph: Graph
    ) -> Dict[str, ThingModelInstance]:

        query_result = thing_models_graph.query(thing_model_discovery_query)
        query_results = query_result_to_dict(query_result)

        thing_models = {}
        for result in query_results:
            thing_model = ThingModelInstance(**result)
            thing_models[thing_model.tm] = thing_model

        return thing_models

    def enrich_interaction_affordance(
        self,
        result: ThingModelDiscoveryResult,
        brownfield_data_graph: Graph,
        thing_description: ThingDescription,
        matching_method: Optional[Callable] = None,
    ) -> Dict:
        thing_model = None
        if settings.enrichment.use_service_enrichment:
            if matching_method is not None:
                thing_model = matching_method(result, self.thing_models_graph)

        if thing_model is not None:

            thing_model = self._thing_models.get(thing_model)

            data = {
                "graph": self.thing_models_graph + brownfield_data_graph,
                "interactionAffordance": thing_model.interactionAffordance,
                "form": thing_model.interactionAffordanceForm,
                "href": result.target,
            }
            thing_description.tms.append(thing_model.tm)
        else:
            # Use the property affordance to create the thing description
            data = {
                "graph": brownfield_data_graph,
                "interactionAffordance": result.interactionAffordanceUri,
                "form": result.interactionAffordanceFormUri,
                "href": result.target,
            }
        return data

    def discover_interaction_affordance(self, data: Dict):

        query_results = data["graph"].query(
            interaction_affordance_query,
            initBindings={"affordance": URIRef(data["interactionAffordance"])},
        )
        query_data = query_result_to_dict(query_results)

        return query_data

    def create_thing(
        self, brownfield_data_graph: Graph, alignment_type: Alignment
    ) -> ThingDescription:
        query_result = query_result_to_dict(
            brownfield_data_graph.query(baseUri_and_title_query)
        )
        if len(query_result) == 0:
            return None

        query_result = query_result[0]

        baseUri = query_result["baseUri"]
        title = query_result["title"]

        thing_description: ThingDescription = ThingDescription(
            baseUri=baseUri, title=title
        )

        matching_method: Optional[Callable] = None

        graph = brownfield_data_graph

        if settings.enrichment.use_service_enrichment:

            matching_method: Callable = get_thing_model_thing_description_matching(
                alignment_type
            )

            graph += self.thing_models_graph

        query_results = query_result_to_dict(
            graph.query(thing_description_discovery_query)
        )
        discoveryResults = [ThingModelDiscoveryResult(**_) for _ in query_results]

        for result in discoveryResults:
            # print("Result Target ID: ", result.target)
            data = self.enrich_interaction_affordance(
                result, brownfield_data_graph, thing_description, matching_method
            )

            interaction_affordance = self.discover_interaction_affordance(data)

            for dat in interaction_affordance:
                affordance = InteractionAffordance(
                    **dat, graph=data["graph"], href=data["href"]
                )
                # Use the thing model to create the thing description
                if (
                    result.affordanceType
                    == InteractionAffordanceType.PROPERTY_AFFORDANCE
                ):
                    thing_description.properties.append(affordance)
                elif (
                    result.affordanceType == InteractionAffordanceType.ACTION_AFFORDANCE
                ):
                    thing_description.actions.append(affordance)
                elif (
                    result.affordanceType == InteractionAffordanceType.EVENT_AFFORDANCE
                ):
                    thing_description.events.append(affordance)

        return thing_description


if __name__ == "__main__":

    thing_models_graph = Graph().parse("./updates/thing_model.ttl", format="turtle")
    thing_factory = ThingFactory(thing_models_graph)

    brownfield_data_graph = Graph().parse(
        "./updates/brownfield_data.ttl", format="turtle"
    )

    thing_description = thing_factory.create_thing(brownfield_data_graph)
