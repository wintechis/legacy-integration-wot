from enum import Enum
from io import BytesIO
from typing import List, Optional

from configs import logger
from pyshacl import validate
from rdflib import Graph


class Alignment(Enum):
    Bluetooth_GATT = "Bluetooth"
    ZIGBEE = "Zigbee"
    ZWAVE = "zWave"
    MATTER = "Matter"


class OntologyAlignment:
    type: Alignment
    ontology: Graph

    def __init__(self, type: Alignment, ontology: Graph):
        self.type = type
        self.ontology = ontology
        logger.debug(f"Ontology alignment {type} loaded.")


class AlignmentFabric:

    def __init__(self, alignments: List[OntologyAlignment]):
        self.alignments = alignments

    def get_alignment(self, type: Alignment) -> Optional[OntologyAlignment]:
        for alignment in self.alignments:
            if alignment.type == type:
                return alignment
        return None

    def process_data(self, data_graph: Graph, identified_alignment: Alignment) -> Graph:
        turtle_data = BytesIO(data_graph.serialize(format="turtle").encode("utf-8"))
        data_graph2 = Graph(store="Oxigraph").parse(turtle_data, format="turtle")

        shacl_alignment = self.get_alignment(identified_alignment)

        r = validate(
            data_graph,
            shacl_graph=shacl_alignment.ontology,
            advanced=True,
            inplace=True,
        )

        conforms, results_graph, results_text = r

        if not conforms:
            logger.error(f"Data does not conform to alignment {identified_alignment}")
            logger.error(results_text)
            return None

        graph = data_graph - data_graph2

        return graph
