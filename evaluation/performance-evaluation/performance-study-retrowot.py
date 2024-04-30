import time

from bluetooth.client import Client as BluetoothClient
from configs import settings
from thing_description.thing_description import ThingDescription
from thing_description_translation import align_capabilities

# Parameters that can be changed
BLUETOOTH_LEGACY_DEVICE_MAC = "F3:82:06:2F:7C:0A"  # Bluetooth legacy device MAC: Needs to be changed based on the device
HCI_DEVICE_LINK = (
    "usb:0a12:0001"  # HCI device link: Needs to be changed based on the device
)
SERVICE_CAPABILITY_SIZE = 100  # Number of service capabilities [1, 10, 20, ..., 100]


async def bluetooth_discovery(client, payload):

    await client.discover_device(payload)
    await client.device_discovery(payload)


async def device_translation(device):
    align_capabilities(device, emitter=None, performance_test=True)


async def transform_to_td(graph):
    td = ThingDescription(graph=graph)
    td.dict()
    return td


async def run_test(test_size: int, frequency: int = 10):

    # Setup a stack for the client
    client = BluetoothClient()

    await client.initalize(
        hci_device_link=HCI_DEVICE_LINK,
        hci_device_name="Bumble",
        hci_device_mac="F0:F1:F2:F3:F4:F5",
    )

    with open("real_device_performance_study_results.txt", "a+") as file:
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
            graph = align_capabilities(device, emitter=None, performance_test=True)
            end_time = time.perf_counter()
            capability_generalization_time = end_time - start_time

            start_time = time.perf_counter()
            td = await transform_to_td(graph)
            end_time = time.perf_counter()
            thing_description_generation_time = end_time - start_time

            settings.enrichment.use_service_enrichment = True
            start_time = time.perf_counter()
            # device.thing_description = ThingDescription(graph=graph)
            td = await transform_to_td(graph)
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


# -----------------------------------------------------------------------------
async def main():
    await run_test(SERVICE_CAPABILITY_SIZE, 50)
