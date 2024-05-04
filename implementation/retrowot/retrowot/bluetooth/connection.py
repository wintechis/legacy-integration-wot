import logging
from bumble.core import ProtocolError, UUID
from bumble.device import Device, Peer
from bumble.gatt_client import ServiceProxy
from typing import List
from bumble.transport import open_transport_or_link
from configs import settings
import asyncio


async def connect(device: Device, target_address: str) -> Peer:
    logging.debug(f'=== Connecting to {target_address}...')
    connection = await device.connect(target_address)
    peer = Peer(connection)    
    logging.debug("Connected")
    return peer

async def disconnect(device: Device, peer: Peer):
    logging.debug(f'=== Disconnecting from {device}...')
    await device.disconnect(peer)
    logging.debug("Disconnected")
    return None
    
    

async def read_value(device, service_id, characteristic_id):
    
    SERVICE_UUID = UUID(service_id)
    CHARACTERISTIC_UUID = UUID(characteristic_id)
    async def read(peer: Peer):
        service = await peer.discover_service(SERVICE_UUID)
        if not service:
            return None
        print("READ")
        if len(service) > 0:
            service: ServiceProxy = service[0]
        
        try:
            value = await peer.read_characteristics_by_uuid(uuid=CHARACTERISTIC_UUID,service=service)
            print(value)
            return value
        except ProtocolError as error:
            print(f'cannot read')
        except TimeoutError:
            print('read timeout')
            
    
    result = await _create_connection(device, read, str(device + service_id + characteristic_id))

    print("Result: ", result)
    return result

async def write_value(device, service_id, characteristic_id, value):
    SERVICE_UUID = UUID(service_id)
    CHARACTERISTIC_UUID = UUID(characteristic_id)
    async def write(peer: Peer):
        service = await peer.discover_service(SERVICE_UUID)
        if len(service) > 0:
            service = service[0]
        
        characteristics = await peer.discover_characteristics([CHARACTERISTIC_UUID], service) 
        #characteritics = peer.get_characteristics_by_uuid(uuid=CHARACTERISTIC_UUID, service=service)
        print(characteristics)
        if len(characteristics) > 0:
            characteristic = characteristics[0]
            try:
                _ = await peer.write_value(attribute=characteristic, value=value)
            except ProtocolError as error:
                print(f'cannot write')
            except TimeoutError:
                print('read timeout')
                    
    
    await _create_connection(device, write, str(device + service_id + characteristic_id))

async def notify(device, service_id, characteristic_id):
    """ For details see: https://arxiv.org/pdf/2211.12934.pdf """
    SERVICE_UUID = UUID(service_id)
    CHARACTERISTIC_UUID = UUID(characteristic_id)

    def on_notify(value):
        print(f"{characteristic_id} VALUE: 0x{value.hex()}")
        
    async def _notify(peer: Peer):
        service = await peer.discover_service(SERVICE_UUID)
        if len(service) > 0:
            service = service[0]
            
        characteristics = await peer.discover_characteristics([CHARACTERISTIC_UUID], service) 
        #characteritics = peer.get_characteristics_by_uuid(uuid=CHARACTERISTIC_UUID, service=service)
        print(characteristics)
        if len(characteristics) > 0:
            characteristic = characteristics[0]
        
            print(characteristic)
            await characteristic.subscribe(on_notify)
            
            #while True:
            #    await asyncio.sleep(1)
    
        
        
    await _create_connection(device, _notify, str(device + service_id + characteristic_id))

DEVICE = None


async def _create_connection(connection_address, function, connection_identifier):
    global DEVICE
    logging.debug('<<< connecting to HCI...')
    
    hci_device_link = settings.hci_device
    hci_device_name = settings.hci_device_name
    hci_device_mac = settings.hci_device_mac
    
    print(hci_device_link)
    async with await open_transport_or_link(hci_device_link) as (hci_source, hci_sink):
        logging.debug('<<< connected')
        #filter_duplicates = len(sys.argv) == 3 and sys.argv[2] == 'filter'

        if DEVICE is None:
            device = Device.with_hci(hci_device_name, hci_device_mac, hci_source, hci_sink)
            DEVICE = device
            await device.power_on()
        else:
            device = DEVICE

     
        #connection_address = '52:56:BE:4C:74:CC' 
                
        connection = await device.connect(connection_address)
        peer = Peer(connection)
        #await asyncio.sleep(3)
        return await function(peer)
        
        
     #   connection_address = '44:C3:2F:72:47:06'
     #   connection = await device.connect(connection_address)
     #   peer = Peer(connection)
     #   await asyncio.sleep(1)
     #   await function(peer)
        
        
        await hci_source.wait_for_termination()

open_peers = {}
async def _create_connection(connection_address, function, connection_identifier):
    global DEVICE
    logging.debug('<<< connecting to HCI...')
    

    #filter_duplicates = len(sys.argv) == 3 and sys.argv[2] == 'filter'

    # Initalize the device
    if DEVICE is None:
        hci_device_link = settings.hci_device
        hci_device_name = settings.hci_device_name
        hci_device_mac = settings.hci_device_mac
        
        print(hci_device_link)
        transport_or_link = await open_transport_or_link(hci_device_link)
        hci_source, hci_sink = await transport_or_link.__aenter__()
        logging.debug('<<< connected')
        device = Device.with_hci(hci_device_name, hci_device_mac, hci_source, hci_sink)
        DEVICE = device
        await device.power_on()
    else:
        device = DEVICE
        print("im here")
    
    # Check if peer is already connected
    if open_peers.get(connection_address) is None:
        connection = await device.connect(connection_address)
        peer = Peer(connection)
        open_peers[connection_address] = peer
    else:
        peer = open_peers[connection_address]
   
    # 
    #await asyncio.sleep(1)
    return await function(peer)
    
    # Here i have to close the connection
    await hci_source.wait_for_termination()
    # Manually call __aexit__ and await it
    await transport_or_link.__aexit__(None, None, None)
    


