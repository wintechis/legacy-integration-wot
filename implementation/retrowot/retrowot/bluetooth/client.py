""" Bluetooth Client Module specifies a client for Bluetooth GATT communication. """
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)

import logging
from typing import Any, Dict, List, MutableSet, Optional, Tuple, Type

import bluetooth.devices as bleDe

# from configs import settings
from bluetooth.devices import AddressType, BLEDevice, BLEDeviceMessage
from bluetooth.service_discovery_enrichment import service_discovery_enrichment
from bumble.company_ids import COMPANY_IDENTIFIERS
from bumble.core import UUID, ProtocolError
from bumble.device import Device, Peer
from bumble.gatt_client import CharacteristicProxy, ServiceProxy
from bumble.hci import Address
from bumble.transport import Transport, open_transport_or_link
from bumble.transport.common import TransportSink, TransportSource


from configs import settings
from pydantic import BaseModel
from pyee import AsyncIOEventEmitter
from utils import SingletonMeta


class DataPoint(BaseModel):
    value: Any
    characteristic: Any
    service: Any
    connection_address: str


class Service:
    def __init__(self) -> None:
        self.proxy: Optional[ServiceProxy] = None
        self.characteristics: Dict[str, CharacteristicProxy] = {}


class ConnectionProfile:
    def __init__(self) -> None:
        self.services: Dict[str, Service] = {}
        self.active_characteristics: Dict[str, CharacteristicProxy] = {}


class Client(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.hci_source: Optional[TransportSource] = None
        self.hci_sink: Optional[TransportSink] = None
        self.device: Optional[Device] = None
        self.transport: Optional[Transport] = None
        self.peers: Dict[str, Peer] = {}
        self.connections: Dict[str, ConnectionProfile] = {}
        self.bluetooth_devices: Dict[str, BLEDevice] = {}
        self.active_connections: MutableSet[str] = set()

    def get_device(self, address: str) -> Optional[BLEDevice]:
        return self.bluetooth_devices.get(address, None)

    def has_active_connection(self, address: str) -> bool:
        return address in self.active_connections

    async def discover_device(self, target_address: str) -> None:
        """Discover Bluetooth LE services, characteristics and descriptors of a device"""

        # print("device_discovery")
        # setup_connection(device, queue)
        await self.device.power_on()
        # print("connect to device")
        # Connect to a peer

        if not self.is_initalized():
            await self.initalize()

        peer = await self.connect(target_address)
        # Get the device information
        ble_device = BLEDevice(
            name=target_address,
            manufacturer_specific_data=b"",
            manufacturer="",
            address=bleDe.Address(
                uuid=target_address,
                address_type=AddressType.PUBLIC,
                static=True,
                resolvable=True,
            ),
            rssi=0,
            data="",
            connectable=True,
            scannable=True,
            anonymous=False,
            legacy=False,
            truncated=False,
            complete=True,
            primary_phy=0,
            secondary_phy=0,
        )
        self.bluetooth_devices[target_address] = ble_device
        await self.disconnect(target_address, peer)

    async def service_discovery(self, target_address: str) -> None:
        """Discover Bluetooth LE services, characteristics and descriptors of a device"""

        # print("device_discovery")
        # setup_connection(device, queue)
        await self.device.power_on()
        # print("connect to device")
        # Connect to a peer

        if not self.is_initalized():
            await self.initalize()

        ble_device = self.bluetooth_devices.get(target_address, None)
        if ble_device is None:
            await self.device_discovery(3)
            ble_device = self.bluetooth_devices.get(target_address, None)

        peer = await self.connect(target_address)
        # Get the device information
        await self._discover_device_information(peer)
        services: List[Service] = await self._extract_device_information(peer)
        ble_device.services = services

        if settings.enrichment.use_service_discovery:
            await service_discovery_enrichment(ble_device, peer)

        await self.disconnect(target_address, peer)

    async def disconnect(self, connection_address: str, peer: Peer):
        """Disconnects a connection with a peer."""
        await peer.connection.disconnect()
        logging.debug(f"Disconnected from {connection_address}")
        self.peers.pop(connection_address, None)

    async def connect(self, connection_address: str) -> Optional[Peer]:
        if not self.is_initalized():
            await self.initalize()

        if connection_address not in self.peers:
            connection = await self.device.connect(connection_address)
            peer = Peer(connection)
            self.peers[connection_address] = peer

        connection = self.peers.get(connection_address, None)

        logging.debug(f"Connected to {connection_address}")
        return connection

    async def _discover_device_information(self, peer: Peer) -> None:
        logging.debug("Discover device information")
        await peer.discover_services()
        await peer.discover_characteristics()
        await peer.discover_descriptors()

    async def _extract_device_information(self, peer: Peer) -> List[Service]:
        """Extract device information from a the connected device."""
        logging.debug("Extract device information")
        services = []
        for service in peer.services:
            characteristics: List[bleDe.Characteristic] = []
            for characteristic in service.characteristics:
                current_characteristic = bleDe.Characteristic(
                    uuid=characteristic.uuid.to_hex_str(),
                    descriptors=[],
                    properties=str(characteristic.properties).split("|"),
                    handle=characteristic.handle,
                )

                descriptors = []
                for descriptor in characteristic.descriptors:
                    try:
                        value = await peer.read_value(descriptor)
                        value = value.hex()
                        discovered_descriptor = bleDe.Descriptor(
                            uuid=descriptor.type, handle=descriptor.handle, value=value
                        )

                        descriptors.append(discovered_descriptor)
                    except ProtocolError as error:
                        logging.debug(f"cannot read {descriptor.handle:04X}:", error)
                    except TimeoutError:
                        logging.debug("read timeout")

                current_characteristic.descriptors = descriptors
                characteristics.append(current_characteristic)

            service = bleDe.Service(
                uuid=service.uuid.to_hex_str(), characteristics=characteristics
            )
            services.append(service)

        logging.debug("Discovered everything")
        return services

    def initialize_advertisment(self):
        def get_manufacturer_specific_data(advertisement) -> Tuple[str, str]:
            data = advertisement.data
            ad = data.get(0xFF)
            if ad:
                manufacturer_specific_data = ad[1]
                manufacturer = COMPANY_IDENTIFIERS.get(ad[0], f"0x{ad[0]:04X}")
                return manufacturer_specific_data, manufacturer
            return "", ""

        def get_name(advertisement) -> str:
            data = advertisement.data
            # 0x09 is the complete local name
            ad = data.get(0x09)
            if ad:
                return ad
            # 0x08 is the short local name
            ad = data.get(0x08)
            if ad:
                return ad

            return ""

        def advertisment_handler(advertisement) -> None:
            logging.debug("New Advertisement: %s", advertisement)

            address_type_string = ("PUBLIC", "RANDOM", "PUBLIC_ID", "RANDOM_ID")[
                advertisement.address.address_type
            ]

            manufacturer_specific_data, manufacturer = get_manufacturer_specific_data(
                advertisement
            )

            if str(advertisement.address) not in self.bluetooth_devices:
                logging.debug(str(advertisement.address))
                device_address: bleDe.Address = bleDe.Address(
                    uuid=str(advertisement.address),
                    address_type=AddressType(address_type_string),
                    static=advertisement.address.is_static,
                    resolvable=advertisement.address.is_resolvable,
                )

                # Check the data for the device name
                name = get_name(advertisement)

                device = BLEDevice(
                    name=name,
                    manufacturer=manufacturer,
                    manufacturer_specific_data=manufacturer_specific_data,
                    address=device_address,
                    rssi=advertisement.rssi,
                    data=advertisement.data.to_string(),
                    connectable=advertisement.is_connectable,
                    scannable=advertisement.is_scannable,
                    anonymous=advertisement.is_anonymous,
                    legacy=advertisement.is_legacy,
                    complete=advertisement.is_complete,
                    truncated=advertisement.is_truncated,
                    primary_phy=advertisement.primary_phy,
                    secondary_phy=advertisement.secondary_phy,
                )
                self.bluetooth_devices[str(advertisement.address)] = device
            else:
                device = self.bluetooth_devices[str(advertisement.address)]

            device_message = BLEDeviceMessage(
                device=device,
                manufacturer_data=manufacturer_specific_data,
                advertisement_data=str(advertisement.data),
                rssi=advertisement.rssi,
            )

            device.messages.append(device_message)

        self.device.on("advertisement", advertisment_handler)

    async def device_discovery(self, sleeping_time: int = 5) -> None:
        if not self.is_initalized():
            await self.initalize()

        await self.power_on()

        await self.device.start_scanning(filter_duplicates=False)

        await asyncio.sleep(sleeping_time)

        await self.device.stop_scanning()

    async def initalize(
        self,
        hci_device_name: str = settings.hci.name,
        hci_device_mac: str = settings.hci.mac,
        hci_device_link: str = settings.hci.link,
        hci_host=None,
    ) -> None:

        if hci_host is None:
            self.transport = await open_transport_or_link(hci_device_link)
            self.hci_source, self.hci_sink = await self.transport.__aenter__()

            self.device = Device.with_hci(
                hci_device_name, Address(hci_device_mac), self.hci_source, self.hci_sink
            )
        else:
            self.device = Device(
                hci_device_name, address=Address(hci_device_mac), host=hci_host
            )

        self.initialize_advertisment()

        await self.power_on()

    def is_initalized(self) -> bool:
        return self.device is not None

    async def power_on(self):
        if self.device.powered_on:
            return
        await self.device.power_on()

    async def power_off(self):
        if not self.device.powered_on:
            return
        await self.device.power_off()
        await self.transport.close()

    async def get_service(
        self, peer: Peer, connection: ConnectionProfile, service_uuid: UUID
    ) -> Service:
        # Check if the service is already discovered
        service = connection.services.get(
            str(service_uuid.to_bytes(force_128=True)), None
        )

        if service is not None:
            return service

        # Else try to find it
        await peer.discover_services()

        for found_service in peer.services:
            logging.debug(found_service.uuid)
            # Add the service to the connection
            _service: Service = Service()
            _service.proxy = found_service
            connection.services[str(found_service.uuid.to_bytes(force_128=True))] = (
                _service
            )

        return connection.services.get(str(service_uuid.to_bytes(force_128=True)), None)

    async def get_characteristic(
        self, peer: Peer, service: Service, characteristic_uuid: UUID
    ) -> CharacteristicProxy:
        # Check if the characteristic is already discovered
        characteristic = service.characteristics.get(
            str(characteristic_uuid.to_bytes(force_128=True)), None
        )

        if characteristic is not None:
            return characteristic

        # Else try to find it
        characteristics = await peer.discover_characteristics((), service.proxy)

        for found_characteristic in characteristics:
            logging.debug(service.characteristics)
            # Add the characteristic to the service
            service.characteristics[
                str(found_characteristic.uuid.to_bytes(force_128=True))
            ] = found_characteristic

        return service.characteristics.get(
            str(characteristic_uuid.to_bytes(force_128=True)), None
        )

    async def discover_characteristic(
        self,
        connection_address: str,
        characteristic_uuid: UUID,
        service_uuid: UUID,
        peer: Peer,
    ) -> CharacteristicProxy:
        connection = self.connections.get(connection_address, None)
        logging.debug("First connection")
        if connection is None:
            connection = ConnectionProfile()
            self.connections[connection_address] = connection

        logging.debug("Number of open connections: ", len(self.connections))

        service = await self.get_service(peer, connection, service_uuid)
        logging.debug(f"Identified Service: {service}")
        if service is None:
            return None

        characteristic = await self.get_characteristic(
            peer, service, characteristic_uuid
        )
        logging.debug(characteristic)
        logging.debug(f"Identified Characteristic: {characteristic}")
        return characteristic

    async def read_value(
        self,
        connection_address: str,
        service_uuid: str,
        characteristic_uuid: str,
        emitter: AsyncIOEventEmitter,
    ):
        SERVICE_UUID = UUID(service_uuid)
        CHARACTERISTIC_UUID = UUID(characteristic_uuid)

        logging.debug(
            f"read_value with service uuid: {SERVICE_UUID} and characteristic uuid: {CHARACTERISTIC_UUID}"
        )

        peer = await self.connect(connection_address)
        self.active_connections.add(connection_address)
        try:
            characteristic = await self.discover_characteristic(
                connection_address, CHARACTERISTIC_UUID, SERVICE_UUID, peer
            )
        except Exception as e:
            logging.debug(e)

        if not characteristic:
            return None

        try:
            value = await peer.read_value(characteristic)
            point = DataPoint(
                value=value,
                characteristic=characteristic,
                service=service_uuid,
                connection_address=connection_address,
            )
            print(
                f"Result of {connection_address}/{service_uuid}/{characteristic}: {value}"
            )
            emitter.emit("read", value)
            return value
        except ProtocolError as error:
            logging.debug(f"cannot read")
        except TimeoutError:
            logging.debug("read timeout")
        finally:
            await self.disconnect(connection_address, peer)
            self.active_connections.remove(connection_address)

    async def write_value(
        self,
        value: Any,
        connection_address: str,
        service_uuid: str,
        characteristic_uuid: str,
        emitter: AsyncIOEventEmitter,
    ):
        self.active_connections.add(connection_address)

        SERVICE_UUID = UUID(service_uuid)
        CHARACTERISTIC_UUID = UUID(characteristic_uuid)

        logging.debug(
            f"write_value: {value} with service uuid: {SERVICE_UUID} and characteristic uuid: {CHARACTERISTIC_UUID}"
        )

        peer = await self.connect(connection_address)

        characteristic = await self.discover_characteristic(
            connection_address, CHARACTERISTIC_UUID, SERVICE_UUID, peer
        )

        if not characteristic:
            return None
        logging.debug("Write")

        try:
            _ = await peer.write_value(attribute=characteristic, value=value)

            point = DataPoint(
                value=True,
                characteristic=characteristic,
                service=service_uuid,
                connection_address=connection_address,
            )

            emitter.emit("write", point)
            return
        except ProtocolError as error:
            logging.debug(f"cannot write")
        except TimeoutError:
            logging.debug("read timeout")
        finally:
            print("in finally")
            await self.disconnect(connection_address, peer)
            self.active_connections.remove(connection_address)

    async def notify(
        self,
        connection_address: str,
        service_uuid: str,
        characteristic_uuid: str,
        emitter: AsyncIOEventEmitter,
    ):
        SERVICE_UUID = UUID(service_uuid)
        CHARACTERISTIC_UUID = UUID(characteristic_uuid)

        print(
            f"notify with service uuid: {SERVICE_UUID} and characteristic uuid: {CHARACTERISTIC_UUID}"
        )

        peer = await self.connect(connection_address)

        print("Connected")
        characteristic = await self.discover_characteristic(
            connection_address, CHARACTERISTIC_UUID, SERVICE_UUID, peer
        )

        if not characteristic:
            return None

        print("Notify")
        print(characteristic)
        print(peer)

        connection = self.connections.get(connection_address, None)

        def on_notify(value):
            try:
                point = DataPoint(
                    value=value,
                    characteristic=characteristic,
                    service=service_uuid,
                    connection_address=connection_address,
                )
                print(value)
                emitter.emit("notify", point)
            except asyncio.CancelledError:
                print("Cancelled")
                return

        print(80 * "=")
        print(f"Characteristic ID: {id(characteristic)}")
        print(f"Characteristic: {characteristic}")
        try:
            _ = await characteristic.subscribe(subscriber=on_notify)
            connection.active_characteristics[characteristic_uuid] = {
                "characterisitic": characteristic,
                "emitter": emitter,
                "subscriber": 1,
            }
            await peer.sustain()

        except ProtocolError as error:
            logging.debug(f"cannot notify")
        except TimeoutError:
            logging.debug("read timeout")

    async def unsubscribe(
        self,
        connection_address: str,
        service_uuid: str,
        characteristic_uuid: str,
        emitter: AsyncIOEventEmitter,
    ):
        SERVICE_UUID = UUID(service_uuid)
        CHARACTERISTIC_UUID = UUID(characteristic_uuid)

        print(
            f"notify with service uuid: {SERVICE_UUID} and characteristic uuid: {CHARACTERISTIC_UUID}"
        )

        peer = await self.connect(connection_address)

        print("Connected")
        characteristic = await self.discover_characteristic(
            connection_address, CHARACTERISTIC_UUID, SERVICE_UUID, peer
        )

        if not characteristic:
            return None

        try:
            _ = await characteristic.unsubscribe(subscriber=emitter)
            await self.disconnect(connection_address=connection_address, peer=peer)
            print("Unsubscribed")

        except ProtocolError as error:
            logging.debug(f"cannot unsubscribe")
        except TimeoutError:
            logging.debug("read timeout")


import asyncio


async def test_subscription_to_multiple_devices():
    # from configs import settings

    from pyee import AsyncIOEventEmitter

    DEVICE_1 = "44:0D:E7:DB:76:BF"
    DEVICE_2 = "F6:98:F1:18:38:36"
    DEVICE_3 = "4C:Df:FB:69:5F:AB"
    c = Client()
    print("Initalize")
    await c.initalize(
        hci_device_link="usb:0a12:0001",
        hci_device_name="Bumble",
        hci_device_mac="F0:F1:F2:F3:F4:F5",
    )
    emitter1 = AsyncIOEventEmitter()

    emitter1.on("read", lambda x: print(x))
    emitter1.on("notify", lambda x: print(x))

    loop = asyncio.get_running_loop()  # Get the running loop
    task_2 = loop.create_task(
        c.read_value(
            connection_address=DEVICE_1,
            service_uuid="00001801-0000-1000-8000-00805f9b34fb",
            characteristic_uuid="00002b3a-0000-1000-8000-00805f9b34fb",
            emitter=emitter1,
        )
    )
    await task_2

    async def job1():
        await asyncio.sleep(3)  # Task takes 3 seconds
        print("Job 1 completed")

    async def job2():
        await asyncio.sleep(1.5)  # Task takes 1.5 seconds
        print("Job 2 completed")

    async def start_after(task, delay):
        await asyncio.sleep(delay)  # Delay the start of the task
        await task

    await asyncio.sleep(1.5)

    emitter2 = AsyncIOEventEmitter()

    emitter2.on("read", lambda x: print(x))
    emitter2.on("notify", lambda x: print(x))
    asyncio.create_task(
        start_after(
            c.notify(
                connection_address=DEVICE_2,
                service_uuid="E95D9882251D470AA062FA1922DFA9A8",
                characteristic_uuid="E95DDA90251D470AA062FA1922DFA9A8",
                emitter=emitter2,
            ),
            3,
        )
    )
    # await task_5

    await asyncio.sleep(1.5)
    loop = asyncio.get_running_loop()  # Get the running loop
    emitter = AsyncIOEventEmitter()

    emitter.on("read", lambda x: print(x))
    emitter.on("notify", lambda x: print(x))
    asyncio.create_task(
        start_after(
            c.notify(
                connection_address=DEVICE_1,
                service_uuid="0000180D-0000-1000-8000-00805f9b34fb",
                characteristic_uuid="00002a37-0000-1000-8000-00805f9b34fb",
                emitter=emitter,
            ),
            3,
        )
    )

    await asyncio.sleep(1.5)
    loop = asyncio.get_running_loop()  # Get the running loop
    emitter3 = AsyncIOEventEmitter()

    emitter3.on("read", lambda x: print(x))
    emitter3.on("notify", lambda x: print(x))
    asyncio.create_task(
        start_after(
            c.notify(
                connection_address=DEVICE_3,
                service_uuid="0000180D-0000-1000-8000-00805f9b34fb",
                characteristic_uuid="00002a37-0000-1000-8000-00805f9b34fb",
                emitter=emitter3,
            ),
            3,
        )
    )

    # await task_7
    await asyncio.sleep(3)
    # await task_3
    # task_4.cancel()
    # task_4.cancel()
    print("Unsubscribe")
    await asyncio.sleep(15)

    #


async def test_multiple_subscriptions():

    # from configs import settings

    from pyee import AsyncIOEventEmitter

    DEVICE_2 = "F6:98:F1:18:38:36"
    c = Client()
    print("Initalize")
    await c.initalize(
        hci_device_link="usb:0a12:0001",
        hci_device_name="Bumble",
        hci_device_mac="F0:F1:F2:F3:F4:F5",
    )
    emitter1 = AsyncIOEventEmitter()

    emitter1.on("read", lambda x: print(x))
    emitter1.on("notify", lambda x: print(x))

    async def job1():
        await asyncio.sleep(3)  # Task takes 3 seconds
        print("Job 1 completed")

    async def job2():
        await asyncio.sleep(1.5)  # Task takes 1.5 seconds
        print("Job 2 completed")

    async def start_after(task, delay):
        await asyncio.sleep(delay)  # Delay the start of the task
        await task

    await asyncio.sleep(1.5)

    emitter1 = AsyncIOEventEmitter()

    emitter1.on("read", lambda x: print(x))
    emitter1.on("notify", lambda x: print(x))
    asyncio.create_task(
        start_after(
            c.notify(
                connection_address=DEVICE_2,
                service_uuid="E95D9882251D470AA062FA1922DFA9A8",
                characteristic_uuid="E95DDA90251D470AA062FA1922DFA9A8",
                emitter=emitter1,
            ),
            3,
        )
    )

    await asyncio.sleep(1.5)

    emitter2 = AsyncIOEventEmitter()

    emitter2.on("read", lambda x: print(x))
    emitter2.on("notify", lambda x: print(x))
    asyncio.create_task(
        start_after(
            c.notify(
                connection_address=DEVICE_2,
                service_uuid="E95D9882251D470AA062FA1922DFA9A8",
                characteristic_uuid="E95DDA91251D470AA062FA1922DFA9A8",
                emitter=emitter2,
            ),
            3,
        )
    )
    # await task_5

    await asyncio.sleep(15)


async def test_unsubscribe():

    # from configs import settings

    from pyee import AsyncIOEventEmitter

    DEVICE_2 = "F6:98:F1:18:38:36"
    c = Client()
    print("Initalize")
    await c.initalize(
        hci_device_link="usb:0a12:0001",
        hci_device_name="Bumble",
        hci_device_mac="F0:F1:F2:F3:F4:F5",
    )
    emitter1 = AsyncIOEventEmitter()

    emitter1.on("read", lambda x: print(x))
    emitter1.on("notify", lambda x: print(x))

    async def job1():
        await asyncio.sleep(3)  # Task takes 3 seconds
        print("Job 1 completed")

    async def job2():
        await asyncio.sleep(1.5)  # Task takes 1.5 seconds
        print("Job 2 completed")

    async def start_after(task, delay):
        await asyncio.sleep(delay)  # Delay the start of the task
        await task

    await asyncio.sleep(1.5)

    emitter1 = AsyncIOEventEmitter()

    emitter1.on("read", lambda x: print(x))
    emitter1.on("notify", lambda x: print(x))
    task_1 = asyncio.create_task(
        c.notify(
            connection_address=DEVICE_2,
            service_uuid="E95D9882251D470AA062FA1922DFA9A8",
            characteristic_uuid="E95DDA90251D470AA062FA1922DFA9A8",
            emitter=emitter1,
        )
    )

    await asyncio.sleep(5)

    # Cancle task and subscription
    asyncio.create_task(
        c.unsubscribe(
            connection_address=DEVICE_2,
            service_uuid="E95D9882251D470AA062FA1922DFA9A8",
            characteristic_uuid="E95DDA90251D470AA062FA1922DFA9A8",
            emitter=emitter1,
        )
    )

    await asyncio.sleep(5)

    await asyncio.sleep(15)


async def test_enrichment():

    # from configs import settings

    DEVICE_2 = "F6:98:F1:18:38:36"
    c = Client()
    print("Initalize")
    await c.initalize(
        hci_device_link="usb:0a12:0001",
        hci_device_name="Bumble",
        hci_device_mac="F0:F1:F2:F3:F4:F5",
    )

    await c.device_discovery(DEVICE_2)

    device = c.get_device(DEVICE_2)

    print(device.to_rdf())


if __name__ == "__main__":
    asyncio.run(test_enrichment())
# asyncio.run(main())
