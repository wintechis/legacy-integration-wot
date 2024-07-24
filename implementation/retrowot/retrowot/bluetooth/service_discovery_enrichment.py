import logging

from bluetooth.devices import BLEDevice, DeviceInformation
from bumble.core import UUID
from bumble.device import Peer
from rdflib import Namespace, URIRef

SBOE = Namespace("https://purl.org/ExtendedSimpleBluetoothOntology#")


async def service_discovery_enrichment(device: BLEDevice, peer: Peer) -> None:
    """Enriches the device with information from the service discovery."""
    logging.info("Enriching device through service discovery...")
    print("Enriching device through service discovery...")

    device.discovered_device_information += [
        await has_device_name(peer),
        await has_system_id(peer),
        await has_model_number(peer),
        await has_serial_number(peer),
        await has_firmware_revision(peer),
        await has_hardware_revision(peer),
        await has_software_revision(peer),
    ]


async def has_device_name(peer: Peer) -> DeviceInformation:
    GENERIC_ACCESS_SERVICE_UUID = UUID("1800")
    DEVICE_NAME_CHARACTERISTIC_UUID = UUID("2A00")

    value = await peer.read_characteristics_by_uuid(
        uuid=DEVICE_NAME_CHARACTERISTIC_UUID
    )
    logging.info(f"Device Name is: {str(value)}")
    print(f"Device Name is: {str(value)}")

    if value == []:
        value = None
    else:
        value = value[0].decode("utf-8")

    return DeviceInformation(information=value, predicate=SBOE.device_name)


async def has_manufacturer_name(peer: Peer) -> DeviceInformation:
    GENERIC_ACCESS_SERVICE_UUID = UUID("1800")
    DEVICE_NAME_CHARACTERISTIC_UUID = UUID("2A29")

    value = await peer.read_characteristics_by_uuid(
        uuid=DEVICE_NAME_CHARACTERISTIC_UUID
    )
    logging.info(f"Device Name is: {str(value)}")
    print(f"Device Name is: {str(value)}")

    if value == []:
        value = None
    else:
        value = value[0].decode("utf-8")

    return DeviceInformation(information=value, predicate=SBOE.manufacturer_name)


async def has_system_id(peer: Peer) -> DeviceInformation:
    """A unique identifier for the device."""
    GENERIC_ACCESS_SERVICE_UUID = UUID("180A")
    DEVICE_NAME_CHARACTERISTIC_UUID = UUID("2A23")

    value = await peer.read_characteristics_by_uuid(
        uuid=DEVICE_NAME_CHARACTERISTIC_UUID
    )
    logging.info(f"Unique Identifier is: {str(value)}")
    print(f"Unique Identifier is: {str(value)}")
    if value == []:
        value = None
    else:
        value = value[0].decode("utf-8")

    return DeviceInformation(information=value, predicate=SBOE.system_id)


async def has_model_number(peer: Peer) -> DeviceInformation:
    GENERIC_ACCESS_SERVICE_UUID = UUID("180A")
    DEVICE_NAME_CHARACTERISTIC_UUID = UUID("2A24")

    value = await peer.read_characteristics_by_uuid(
        uuid=DEVICE_NAME_CHARACTERISTIC_UUID
    )
    logging.info(f"Model Number is: {str(value)}")
    print(f"Model Number is: {str(value)}")
    if value == []:
        value = None
    else:
        value = value[0].decode("utf-8")

    return DeviceInformation(information=value, predicate=SBOE.model_number)


async def has_serial_number(peer: Peer) -> DeviceInformation:
    GENERIC_ACCESS_SERVICE_UUID = UUID("180A")
    DEVICE_NAME_CHARACTERISTIC_UUID = UUID("2A25")

    value = await peer.read_characteristics_by_uuid(
        uuid=DEVICE_NAME_CHARACTERISTIC_UUID
    )
    logging.info(f"Serial Number is: {str(value)}")
    print(f"Serial Number is: {str(value)}")
    if value == []:
        value = None
    else:
        value = int(value[0])

    return DeviceInformation(information=value, predicate=SBOE.serial_number)


async def has_firmware_revision(peer: Peer) -> DeviceInformation:
    GENERIC_ACCESS_SERVICE_UUID = UUID("180A")
    DEVICE_NAME_CHARACTERISTIC_UUID = UUID("2A26")

    value = await peer.read_characteristics_by_uuid(
        uuid=DEVICE_NAME_CHARACTERISTIC_UUID
    )
    logging.info(f"Firmware Version is: {str(value)}")
    print(f"Firmware Version is: {str(value)}")
    if value == []:
        value = None
    else:
        value = value[0].decode("utf-8")

    return DeviceInformation(information=value, predicate=SBOE.firmware_revision)


async def has_hardware_revision(peer: Peer) -> DeviceInformation:
    GENERIC_ACCESS_SERVICE_UUID = UUID("180A")
    DEVICE_NAME_CHARACTERISTIC_UUID = UUID("2A27")

    value = await peer.read_characteristics_by_uuid(
        uuid=DEVICE_NAME_CHARACTERISTIC_UUID
    )
    logging.info(f"Software Version is: {str(value)}")
    print(f"Hardware Version is: {str(value)}")
    if value == []:
        value = None
    else:
        value = value[0].decode("utf-8")

    return DeviceInformation(information=value, predicate=SBOE.hardware_revision)


async def has_software_revision(peer: Peer) -> DeviceInformation:
    GENERIC_ACCESS_SERVICE_UUID = UUID("180A")
    DEVICE_NAME_CHARACTERISTIC_UUID = UUID("2A28")

    value = await peer.read_characteristics_by_uuid(
        uuid=DEVICE_NAME_CHARACTERISTIC_UUID
    )
    logging.info(f"Software Version is: {str(value)}")
    print(f"Software Version is: {str(value)}")
    if value == []:
        value = None
    else:
        value = value[0].decode("utf-8")

    return DeviceInformation(information=value, predicate=SBOE.software_revision)
