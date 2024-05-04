import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)
from typing import List, Dict, Any, Optional, Type, Tuple, MutableSet, Union

from configs import settings
from utils import SingletonMeta
from zigpy.application import ControllerApplication
import asyncio
import zigpy
from pydantic import BaseModel
from logging import getLogger
import zigpy.types
from pyee import AsyncIOEventEmitter

from zigbee.device import ZigbeeDevice
from zigbee.datamodel import (
    Endpoint,
    InCluster,
    OutCluster,
    Attribute,
    Command,
    ClientCommand,
    ServerCommand,
)
import zigpy.types as t
from zigpy.zcl import foundation

logger = getLogger("Logger")


class ZigbeeClient(metaclass=SingletonMeta):
    devices: Dict[str, Any] = {}
    controller: ControllerApplication = None

    def __init__(self):
        self.devices: Dict[str, Any] = {}
        self._devices: Dict[str, Any] = {}
        self.is_active = False
        
    async def service_discovery(self, device: Any):
        await self.discover_attributes(device)
        return device

     
    async def discover_attributes(self, device: ZigbeeDevice):
        def get_access_types(access: int) -> List[str]:
                access_types = []
                if access & zigpy.zcl.foundation.AttributeAccessControl.READ:
                    access_types.append("READ")
                if access & zigpy.zcl.foundation.AttributeAccessControl.WRITE:
                    access_types.append("WRITE")
                if access & zigpy.zcl.foundation.AttributeAccessControl.REPORT:
                    access_types.append("REPORT")
                return access_types
        
        for endpoint in device.endpoints:
            # print("Endpoint ID is: ", hex(endpoint.name))
            
            for _cluster in endpoint.clusters:
                cluster: zigpy.Cluster.Cluster = _cluster.zigpy_cluster
                for _ in range(0, 3):
                    try:
                        extended_attribute_rsp = await cluster.discover_attributes_extended(0, 255)
                        try:
                        
                            for attr in extended_attribute_rsp.extended_attr_info:
                                discovered_attribute = Attribute(name=str(attr.attrid),
                                        properties=get_access_types(attr.acl),
                                        id=attr.attrid,
                                        type=attr.datatype)
                                
                                _cluster.attributes.append(discovered_attribute)
                               #  print(f"Discovered Attribute: {discovered_attribute}")
                            break
                        except Exception as e:
                            print(e)
                            break
                            
                    except asyncio.TimeoutError:
                        print("Timeout")
                        continue
    
    async def discover_commands(self, ieee: str):
        device = self.get_zigbee_device(ieee)
        
        commands = []
        for endpoint in device.endpoints.values():
            
            ep: zigpy.endpoint.Endpoint = endpoint
            if isinstance(endpoint, zigpy.zdo.ZDO):
                continue

            
            for cluster in endpoint.in_clusters.values():
                in_cluster: zigpy.Cluster.Cluster = cluster

                result = []
                for i in range(0, 3):
                    try:
                        result = await cluster.discover_commands_generated(0, 255)
                        print(result)
                        result = result
                        break
                    except asyncio.TimeoutError:
                        logger.debug("Timeout")
                        continue
                
                logger.debug(result)
                commands += result



    async def device_discovery(self, timeout: int = 5) -> List[str]:
        task = asyncio.create_task(self.scan_zigbee(timeout))
        await asyncio.sleep(timeout)
        await task
        return list(self._devices.keys())

    def _add_listener(self):
        class ZigbeeListener:
            def __init__(
                self,
                za: ControllerApplication,
                client: "ZigbeeClient",
                ext_callback: callable = None,
            ):
                logger.debug(
                    f"ZigbeeListenerClass init with ControllerApplication: {za}, and Callback: {ext_callback}"
                )
                self.za = za
                self.client = client
                self.ext_callback = ext_callback

            """
            These are called by the ControllerApplication using call like this: 
            self.listener_event("raw_device_initialized", device)
            """

            def raw_device_initialized(self, device: zigpy.device.Device):

                endpoints = []
                for endpoint in device.endpoints.values():
                    if isinstance(endpoint, zigpy.zdo.ZDO):
                        continue
                    _endpoint = Endpoint(name=endpoint.profile_id, clusters=[])
                    for cluster in endpoint.in_clusters.values():
                        print(cluster)
                        _cluster = InCluster(
                            name=cluster.name,
                            cluster_id=cluster.cluster_id,
                            attributes=[],
                            commands=self._add_commands(cluster),
                            zigpy_cluster=cluster,
                        )

                        _endpoint.clusters.append(_cluster)

                    # OutCluster is currently not really relevant.
                    for cluster in endpoint.out_clusters.values():
                        print(cluster)
                        _cluster = OutCluster(
                            name=cluster.name,
                            cluster_id=cluster.cluster_id,
                            attributes=[],
                            commands=self._add_commands(cluster),
                            zigpy_cluster=cluster,
                        )

                        _endpoint.clusters.append(_cluster)

                    endpoints.append(_endpoint)

                device = ZigbeeDevice(
                    ieee=str(device.ieee),
                    nwk=device.nwk,
                    manufacturer=device.manufacturer,
                    manufacturer_id=device.manufacturer_id,
                    model=device.model,
                    endpoints=endpoints,
                )
                logger.debug(f"ZigbeeDevice '{device.ieee}' with {len(device.endpoints)} endpoints created")
                self.client._devices[device.ieee] = device

            def _add_attributes(self, cluster) -> List[Attribute]:
                # Deprecated: These are not real attributes provided by the device, but assumed ones by the library.
                attributes = []

                def get_access_types(access: int) -> List[str]:
                    access_types = []
                    if access & zigpy.zcl.foundation.ZCLAttributeAccess.Read:
                        access_types.append("READ")
                    if access & zigpy.zcl.foundation.ZCLAttributeAccess.Write:
                        access_types.append("WRITE")
                    if access & zigpy.zcl.foundation.ZCLAttributeAccess.Write_Optional:
                        access_types.append("WRITE_OPTIONAL")
                    if access & zigpy.zcl.foundation.ZCLAttributeAccess.Report:
                        access_types.append("REPORT")
                    return access_types

                for attribute in cluster.attributes.values():
                    attribute = Attribute(
                        name=attribute.name,
                        properties=get_access_types(attribute.access),
                        id=attribute.id,
                        type=None,  # attribute.type,
                    )
                    attributes.append(attribute)
                return attributes

            def _add_commands(self, cluster) -> List[Command]:
                commands = []
                for command in cluster.client_commands.values():
                    print(command)
                    command = ClientCommand(
                        name=command.name, properties=[], id=command.id, type=None
                    )
                    commands.append(command)
                print("Server commands")
                for command in cluster.server_commands.values():
                    print(command)
                    command = ServerCommand(
                        name=command.name, properties=[], id=command.id, type=None
                    )
                    commands.append(command)
                return commands

        listener = ZigbeeListener(self.controller, self)
        self.controller.add_listener(listener)
        self.controller.groups.add_listener(listener)
        logger.debug("Zigbee listener initialized")

    def _init_db(self, add_db: bool = False):
        file_path = settings.zigbee.database
        if add_db:
            try:
                open(file_path, "a").close()
            except OSError:
                logger.info("Failed creating the file")
            else:
                logger.info("File created")

    async def start_zigbee(self, add_db: bool = False):
        match settings.zigbee.radio_type:
            case "ezsp":
                from bellows.zigbee.application import ControllerApplication

                print("Imported bellows")
            case "xbee":
                from zigpy_xbee.zigbee.application import ControllerApplication
            case "deconz":
                from zigpy_deconz.zigbee.application import ControllerApplication
            case "zstack":
                from zigpy_zstack.zigbee.application import ControllerApplication
            case _:
                raise ValueError(
                    f"Controller {settings.zigbee.radio_type} not supported"
                )

        self._init_db(add_db)
        config = ControllerApplication.SCHEMA(
            {
                "device": {
                    "path": settings.zigbee.device_path,
                    "baudrate": settings.zigbee.baurate,
                },
                "database_path": settings.zigbee.database,
                "use_thread": False,
                "startup_energy_scan": False,
                "backup_enabled": False,
                "flow_control": "software",
            }
        )

        self.controller = await ControllerApplication.new(
            config=config, auto_form=True, start_radio=True
        )

        self.is_active = True


        self._add_listener()
        return

    async def shutdown_zigbee(self, remove_db: bool = False):
        """Shutdown the Zigbee network."""

        if remove_db:
            import os, errno

            try:
                os.remove(settings.zigbee.database)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
        if not self.is_active:
            return

        logger.debug("Shutting down Zigbee network")
        await self.controller.shutdown()
        self.is_active = False
        logger.debug("Zigbee network shutdown")

    async def scan_zigbee(self, pairing_timeout=settings.zigbee.pairing_timeout):
        """Scan for Zigbee devices."""
        logger.debug("Scanning for Zigbee devices")
        if not self.is_active:
            raise RuntimeError("Zigbee network not initialized")

        if pairing_timeout < 0:
            logger.debug("Zigbee network is pairing indefinitely")
            while True:
                await self.controller.permit(time_s=254)

        else:
            if pairing_timeout > 254:
                pairing_timeout = 254
            logger.debug("Zigbee network is pairing for %s seconds", pairing_timeout)
            await self.controller.permit(time_s=pairing_timeout)

        logger.debug("Scanning for Zigbee devices complete")

    def _init_zigbee_config(self):
        ControllerApplication.SCHEMA(
            {
                "device": {
                    "path": settings.zigbee.device_path,
                    "baudrate": settings.zigbee.baurate,
                },
                "database": settings.zigbee.database,
                "use_thread": False,
                "startup_energy_scan": False,
            }
        )

    def _import_library(self, controller: str = settings.zigbee.radio_type):
        logger.debug(f"Importing library for controller: {controller}")

    async def _info(self):
        # await self.controller.connect()
        app = self.controller
        await app.load_network_info(load_devices=False)

        logger.debug(f"PAN ID:                0x{app.state.network_info.pan_id:04X}")
        logger.debug(f"Extended PAN ID:       {app.state.network_info.extended_pan_id}")
        logger.debug(f"Channel:               {app.state.network_info.channel}")
        logger.debug(f"Channel mask:          {list(app.state.network_info.channel_mask)}")
        logger.debug(f"NWK update ID:         {app.state.network_info.nwk_update_id}")
        logger.debug(f"Device IEEE:           {app.state.node_info.ieee}")
        logger.debug(f"Device NWK:            0x{app.state.node_info.nwk:04X}")
        logger.debug(f"Network key:           {app.state.network_info.network_key.key}")
        logger.debug(f"Network key sequence:  {app.state.network_info.network_key.seq}")
        logger.debug(f"Network key counter:   {app.state.network_info.network_key.tx_counter}")

    async def read_attribute(
        self,
        ieee: str = "",
        endpoint_id: str = '1',
        cluster_id: str = '0',
        attribute_id: str = '0',
        emitter: AsyncIOEventEmitter = None
    ) -> Any:
        """
        Updates the attribute for a specific cluster in the Zigbee client. 
        It allows to add an emitter to the function for further processing of the data.

        Args:
            ieee (str): The IEEE address of the device.
            endpoint_id (str): The endpoint ID of the device.
            cluster_id (str): The cluster ID of the device.
            command_id (str): The command ID of the device.

        Returns:
            None

        Example:
            >>> from pyee import AsyncIOEventEmitter
            >>> emitter = AsyncIOEventEmitter()
            >>> client = ZigbeeClient()
            >>> ieee_address = "0011223344556677"
            >>> device = client.get_zigbee_device(ieee_address)           
            >>> await client.read_attribute(ieee='00:11:22:33:44:55:66:77', endpoint_id='0x0001', cluster_id='0x0006', attribute_id='0x0000', emitter='emitter')
        """
        cluster = self.get_cluster(ieee, endpoint_id, cluster_id)
        

        # Convert the hex-string command_id to integer
        attribute_id = int(attribute_id, 16) 
        _result = await cluster.read_attributes_raw([attribute_id])

        result = _result[0][0].value.serialize()

        emitter.emit("read", result)

    async def write_attribute(
        self,
        ieee: str = "",
        endpoint_id: str = '1',
        cluster_id: str = '0',
        attribute_id: str = '0',
        value: int = 0,
        emitter: AsyncIOEventEmitter = None
    ):
        """
        Updates the attribute for a specific cluster in the Zigbee client. 
        It allows to add an emitter to the function for further processing of the data.

        Args:
            ieee (str): The IEEE address of the device.
            endpoint_id (str): The endpoint ID of the device.
            cluster_id (str): The cluster ID of the device.
            command_id (str): The command ID of the device.

        Returns:
            None

        Example:
            >>> from pyee import AsyncIOEventEmitter
            >>> emitter = AsyncIOEventEmitter()
            >>> client = ZigbeeClient()
            >>> ieee_address = "0011223344556677"
            >>> device = client.get_zigbee_device(ieee_address)           
            >>> await client.write_attribute(ieee='00:11:22:33:44:55:66:77', endpoint_id='0x0001', cluster_id='0x0006', attribute_id='0x0000', value='0x00', emitter='emitter')
        """

        cluster = self.get_cluster(ieee, endpoint_id, cluster_id)
        
        # Convert the hex-string command_id to integer
        attribute_id = int(attribute_id, 16) 
        result = await cluster.write_attributes_raw({int(attribute_id): value})
        
        emitter.emit("write", result)

    async def update_command(
                self,
                ieee: str = "",
                endpoint_id: str = '1',
                cluster_id: str = '0',
                command_id: str = '0x00',
            ) -> None:
            """
            Creates an command for a specific cluster in the Zigbee client.

            Args:
                ieee (str): The IEEE address of the device.
                endpoint_id (str): The endpoint ID of the device.
                cluster_id (str): The cluster ID of the device.
                command_id (str): The command ID of the device.

            Returns:
                None

            Example:
                >>> client = ZigbeeClient()
                >>> ieee_address = "0011223344556677"
                >>> device = client.get_zigbee_device(ieee_address)           
                >>> await client.update_command(ieee='00:11:22:33:44:55:66:77', endpoint_id='0x0001', cluster_id='0x0006', command_id='0x01')
            """
            
            cluster = self.get_cluster(ieee, endpoint_id, cluster_id)  
            
            # Convert the hex-string command_id to integer
            command_id = int(command_id, 16) 
            
            await cluster.command(command_id)

    def get_cluster(
        self, ieee: str, endpoint_id: str, cluster_id: str
    ) -> zigpy.zcl.Cluster:
        """
        Retrieves the Zigbee cluster associated with the specified endpoint and cluster IDs as hexstrings.

        Args:
            ieee (str): The IEEE address of the Zigbee device.
            endpoint_id (str): The ID of the endpoint as hexstring.
            cluster_id (str): The ID of the cluster as hexstring.

        Returns:
            zigpy.zcl.Cluster: The Zigbee cluster object.

        Raises:
            RuntimeError: If the Zigbee network is not initialized.
            
        Example:
            >>> client = ZigbeeClient()
            >>> ieee_address = "0011223344556677"
            >>> device = client.get_zigbee_device(ieee_address)
            >>> cluster = client.get_cluster(device, "0x0104", "0x006") # 0x0104 = ZCL_HomeAutomation, 0x006 = OnOff
        """
        if not self.is_active:
            raise RuntimeError("Zigbee network not initialized")

        # Convert the hexstrings back to integers
        endpoint_id = int(endpoint_id, 16)
        cluster_id = int(cluster_id, 16)
        device = self.get_zigbee_device(ieee)
        print(device.endpoints)
        
        endpoint = None
        for _endpoint in device.endpoints.values():
            print(_endpoint)
            
            if isinstance(_endpoint, zigpy.zdo.ZDO):
                continue
            print(_endpoint.profile_id)
            if endpoint_id == _endpoint.profile_id:
                endpoint = _endpoint
                break
        
        cluster = endpoint.in_clusters[cluster_id]
        return cluster

    def get_zigbee_device(self, ieee: str) -> zigpy.device.Device:
        """
        Retrieves a Zigpy Zigbee device with its functions based on its IEEE address.

        Args:
            ieee (str): The IEEE address of the Zigbee device.

        Returns:
            zigpy.device.Device: The Zigbee device object.

        Example:
            >>> client = ZigbeeClient()
            >>> ieee_address = "0011223344556677"
            >>> device = client.get_zigbee_device(ieee_address)
        """

        if not self.is_active:
            raise RuntimeError("Zigbee network not initialized")
        ieee = zigpy.types.EUI64.convert(ieee)
        device = self.controller.get_device(ieee)
        return device

    def get_device(self, ieee: str) -> ZigbeeDevice:
        """
        Retrieves a shallow Zigbee device based on its IEEE address.

        Args:
            ieee (str): The IEEE address of the device.

        Returns:
            ZigbeeDevice: The Zigbee device object.

        Examples:
            >>> client = ZigbeeClient()
            >>> device = client.get_device("00:11:22:33:44:55:66:77")
            >>> print(device)
            ZigbeeDevice(name="Device1", ieee="00:11:22:33:44:55:66:77", type="Sensor")
        """
        if not self.is_active:
            raise RuntimeError("Zigbee network not initialized")

        device = self._devices.get(ieee, None)
        return device

async def main():
    print(settings)
    c = ZigbeeClient()
    print("Starting Zigbee")
    await c.start_zigbee(add_db=True)
    emitter = AsyncIOEventEmitter()
    
    emitter.on("read", lambda x: print("Read:", x)) 
    add_new_device = True

    if add_new_device:
        print("Scanning Zigbee")
        task = asyncio.create_task(c.scan_zigbee(10))
        await asyncio.sleep(10)
        await task

    await c.service_discovery(c.get_device("a4:c1:38:96:69:6d:a8:18"))
    #await c.discover_attributes("a4:c1:38:96:69:6d:a8:18")
    #await c.discover_commands("a4:c1:38:96:69:6d:a8:18")
    command = '0x01'
    while True:
        for i in range(3):
            try:
                await c.read_attribute(ieee="a4:c1:38:96:69:6d:a8:18",
                                    endpoint_id="0x0104",
                                    cluster_id="0x006",
                                    attribute_id="0x000",
                                    emitter=emitter)
                
                await asyncio.sleep(0.5)
            except:
                print("Timeout")
                continue
        
        if int(command,16) == 1:
            command = "0x0000"
        else:
            command = '0x0001'

        for i in range(3):
            try:
                await c.update_command("a4:c1:38:96:69:6d:a8:18", "0x0104", "0x006", command)
            except asyncio.TimeoutError:
                print("Timeout")
                continue
            break
        await asyncio.sleep(0.1)
        
        
    command = 0x01
    while True:
        for i in range(3):
            try:
                value = await c.read_attribute("a4:c1:38:96:69:6d:a8:18", 260, 6, 0x0000, emitter)
            except asyncio.TimeoutError:
                print("Timeout")
                continue
            break
        if value:
            print(80 * "-")
            print(value[0][0].value)
        await asyncio.sleep(2)

        if command == 0x01:
            command = 0x00
        else:
            command = 0x01
        print(command)
        for i in range(3):
            try:
                await c.update_command("a4:c1:38:96:69:6d:a8:18", 260, 6, command)
            except asyncio.TimeoutError:
                print("Timeout")
                continue
            break
        await asyncio.sleep(0.1)



    
    
    print("Shutting down Zigbee")
    await c.shutdown_zigbee(remove_db=True)
    return


    device = c.controller.get_device(ieee)
    print(80 * "-")
    print(device.endpoints)
    print(80 * "-")
    endpoint = device.endpoints[1]

    print(endpoint.in_clusters)
    print(80 * "-")
    cluster = endpoint.in_clusters[6]
    result = await cluster.read_attributes_raw([0x0000])
    print(80 * "-")
    print(result)
    print(80 * "-")
    print(result[0])
    print(80 * "-")
    print(result[0][0])

    print(80 * "-")
    print()
    result = await cluster.command(0x01)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
