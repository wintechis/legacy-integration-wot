import asyncio
import time

from bluetooth.client import Client as BluetoothClient
from configs import settings
from rdflib import Graph
from thing_description.ontology_alignment import (
    Alignment,
    AlignmentFabric,
    OntologyAlignment,
)
from thing_description.thing_description_factory import ThingFactory

# Parameters that can be changed
BLUETOOTH_LEGACY_DEVICE_MAC = "F3:82:06:2F:7C:0A"  # Bluetooth legacy device MAC: Needs to be changed based on the device
HCI_DEVICE_LINK = (
    "usb:0a12:0001"  # HCI device link: Needs to be changed based on the device
)
SERVICE_CAPABILITY_SIZE = 30  # Number of service capabilities [1, 10, 20, ..., 100]

alignment_fabric = AlignmentFabric(
    [
        OntologyAlignment(
            Alignment.Bluetooth_GATT,
            Graph(store="Oxigraph").parse(
                "./retrowot/alignments/bluetooth_gatt_alignments.ttl"
            ),
        )
    ]
)
alignment_type = Alignment.Bluetooth_GATT

thing_models = Graph(store="Oxigraph").parse(
    "./retrowot/thing_models/bluetooth_thing_models.ttl"
)
thing_fabric = ThingFactory(thing_models)


async def bluetooth_discovery(client, payload):

    await client.discover_device(payload)
    await client.service_discovery(payload)


async def device_information_translation(device):
    g_device = device.to_rdf()
    aligned_data = alignment_fabric.process_data(g_device, alignment_type)
    return aligned_data


async def transform_to_td(graph):
    thing_description = thing_fabric.create_thing(graph, alignment_type)
    td = thing_description.to_json_ld()
    return td


async def run_test(test_size: int, frequency: int = 10):

    # Setup a stack for the client
    client = BluetoothClient()

    await client.initalize(
        hci_device_link=HCI_DEVICE_LINK,
        hci_device_name="Bumble",
        hci_device_mac="F0:F1:F2:F3:F4:F5",
    )

    with open("performance_study_results.txt", "a+") as file:
        file.write("Test size: " + str(test_size) + "\n")
        print("Test size: ", test_size)
        for i in range(frequency):
            print("Measurement: ", i)
            settings.enrichment.use_service_enrichment = False

            start_time = time.perf_counter()
            # Connect the client to the server
            await bluetooth_discovery(client, BLUETOOTH_LEGACY_DEVICE_MAC)
            device = client.get_device(BLUETOOTH_LEGACY_DEVICE_MAC)
            end_time = time.perf_counter()
            discovery_time = end_time - start_time

            start_time = time.perf_counter()
            g_device = await device_information_translation(device)

            end_time = time.perf_counter()
            capability_generalization_time = end_time - start_time

            start_time = time.perf_counter()
            raw_td = await transform_to_td(g_device)
            end_time = time.perf_counter()
            thing_description_generation_time = end_time - start_time

            settings.enrichment.use_service_enrichment = True
            start_time = time.perf_counter()
            # device.thing_description = ThingDescription(graph=graph)
            enriched_td = await transform_to_td(g_device)

            end_time = time.perf_counter()
            thing_description_generation_with_enrichment_time = end_time - start_time
            enrichment_time = (
                thing_description_generation_with_enrichment_time
                - thing_description_generation_time
            )

            file.write("Discovery Time: " + str(discovery_time) + "\n")
            file.write(
                "Capability Generalization Time: "
                + str(capability_generalization_time)
                + "\n"
            )
            file.write("Capability Enrichment Time: " + str(enrichment_time) + "\n")
            file.write(
                "Thing Description Generation Time: "
                + str(thing_description_generation_time)
                + "\n"
            )

            file.write(
                "Overall Time: "
                + str(
                    discovery_time
                    + capability_generalization_time
                    + enrichment_time
                    + thing_description_generation_time
                )
                + "\n"
            )

            with open("raw_td.json", "w") as f:
                f.write(str(raw_td))

            with open("enriched_td.json", "w") as f:
                f.write(str(enriched_td))


# -----------------------------------------------------------------------------
async def main():
    await run_test(SERVICE_CAPABILITY_SIZE, 4)


if __name__ == "__main__":
    asyncio.run(main())
