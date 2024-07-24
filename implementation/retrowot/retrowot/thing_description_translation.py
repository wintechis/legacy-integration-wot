from base_models import Device
from bluetooth.devices import BLEDevice
from pyshacl import validate
from rdflib import Graph
from thing_description.models import ThingDescription
from zigbee.device import ZigbeeDevice

from retrowot.configs import logger, settings
from retrowot.thing_description.ontology_alignment import (
    Alignment,
    AlignmentFabric,
    OntologyAlignment,
)
from retrowot.thing_description.thing_description_factory import ThingFactory

alignment_fabric = AlignmentFabric(
    [
        OntologyAlignment(
            Alignment.Bluetooth_GATT,
            Graph().parse(settings.alignments.bluetooth_alignments_path),
        ),
        OntologyAlignment(
            Alignment.ZIGBEE,
            Graph().parse(settings.alignments.zigbee_alignments_path),
        ),
    ]
)

bluetooth_thing_models = Graph().parse(
    settings.thing_models.bluetooth_thing_models_path
)
zigbee_thing_models = Graph().parse(settings.thing_models.zigbee_thing_models_path)
thing_models = bluetooth_thing_models + zigbee_thing_models

thing_fabric = ThingFactory(thing_models)


def get_alignment_type(device: Device):
    # Determine the alignment type of a device based on the device's capabilities
    if isinstance(device, ZigbeeDevice):
        logger.debug("Device is a Zigbee device")
        return Alignment.ZIGBEE
    elif isinstance(device, BLEDevice):
        logger.debug("Device is a Bluetooth device")
        return Alignment.Bluetooth_GATT
    else:
        raise ValueError("Device type not supported")


def align_capabilities(device: Device, emitter=None, performance_test: bool = False):
    # Maps the capabilities of a device to the corresponding affordances

    g_device = device.to_rdf()
    alignment_type = get_alignment_type(device)

    aligned_data = alignment_fabric.process_data(g_device, alignment_type)

    emitter.emit("raw_device_data_aligned", device)

    thing_description = thing_fabric.create_thing(aligned_data, alignment_type)

    if performance_test:
        return g_device

    device.thing_description = thing_description

    emitter.emit("thing_description_created", device)
    emitter.emit("add_thing_description_to_thing_directory", device)


if __name__ == "__main__":
    graph = Graph().parse("./BBC micro:bit [geto.ttl", format="turtle")

    shacl_graph = Graph().parse("./servicetranslation.ttl")

    validate(graph, shacl_graph=shacl_graph, advanced=True, inplace=True)
    graph.serialize("enriched_test.ttl", format="turtle")
    td = ThingDescription(graph)
