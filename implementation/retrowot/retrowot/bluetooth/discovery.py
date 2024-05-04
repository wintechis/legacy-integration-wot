# Tasks:
# Scan for bluetooth devices
# Connect to a bluetooth device
# Discover services, characteristics and descriptors
# Discover device attributes


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import asyncio
import os
import logging

from bumble.core import ProtocolError
from bumble.device import Device, Peer
from bumble.transport import open_transport_or_link
from configs import settings

from bluetooth.devices import AddressType, Address, BLEDevice, BLEDeviceMessage, Service, Characteristic, Descriptor

from bluetooth.connection import connect, disconnect

from typing import List



async def service_discovery(queue: dict, target_address: str, current_device) -> List[Service]:
    '''Discover Bluetooth LE services, characteristics and descriptors of a device'''
    async with await open_transport_or_link(settings.hci.link) as (hci_source, hci_sink):
        logging.debug('Connected to HCI link' )

        # Create a HCI device instance
        device = Device.with_hci(settings.hci.name, settings.hci.mac, hci_source, hci_sink)
          
        #setup_connection(device, queue)
        await device.power_on()

        # Connect to a peer
        peer = await connect(device, target_address)
       
        # Get the device information
        await discover_device_information(peer)
        services: List[Service] = await extract_device_information(peer)
        
            
        queue[target_address] = services
       
        current_device.services = services
        
        print("Disconnect")
        await disconnect(device, peer)
        
        
        # Shutdown the device 
        await device.power_off()
        

async def device_discovery(queue: dict, device_discovery_duration = settings.bluetooth.device_discovery_timeout) -> None:
    '''Discover Bluetooth LE devices'''
    async with await open_transport_or_link(settings.hci.link) as (hci_source, hci_sink):
        logging.debug('Connected to HCI link' )

        # Create a HCI device instance
        device = Device.with_hci(settings.hci.name, settings.hci.mac, hci_source, hci_sink)
        
        # Update device advertisement event
        setup_advertisment(device, queue)
        
        
        await device.power_on()
        await device.start_scanning(filter_duplicates=False)

        await asyncio.sleep(device_discovery_duration)
        await device.stop_scanning()
        
        

def setup_advertisment(device: Device, queue: dict) -> None:
    
    @device.on('advertisement')
    def _(advertisement):
        logging.debug("New Advertisement: %s", advertisement)
        print("new Advertisment")
        address_type_string = ('PUBLIC', 'RANDOM', 'PUBLIC_ID', 'RANDOM_ID')[
            advertisement.address.address_type
        ]
        
        device_address: Address = Address(
                                    uuid=str(advertisement.address),
                                    address_type=AddressType(address_type_string),
                                    static=advertisement.address.is_static,
                                    resolvable=advertisement.address.is_resolvable)
        
        
        device = BLEDevice(
                    # name=device.name,
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
                    secondary_phy=advertisement.secondary_phy)
        
        
        device_message = BLEDeviceMessage(device=device)
        
        
        if device.address.uuid not in queue:
            queue[device.address.uuid] = [device_message]
        else:
            queue[device.address.uuid].append(device_message)
        
        
        

 


async def discover_device_information(peer: Peer) -> None:
    logging.debug("Discover device information")
    await peer.discover_services()
    await peer.discover_characteristics()
    await peer.discover_descriptors()


async def extract_device_information(peer: Peer) -> List[Service]:
    ''' Extract device information from a the connected device. '''
    logging.debug("Extract device information")
    services = []
    for service in peer.services:
 
        characteristics: List[Characteristic] = []
        for characteristic in service.characteristics:
            current_characteristic = Characteristic(uuid=characteristic.uuid.to_hex_str(),
                            descriptors=[],
                            properties=[str(characteristic.properties)],
                            handle=characteristic.handle)
            
            descriptors = []
            for descriptor in characteristic.descriptors:
                try:
                    value = await peer.read_value(descriptor)
                    value = value.hex()
                    discovered_descriptor = Descriptor(
                        uuid=descriptor.type,
                        handle=descriptor.handle,
                        value=value                           
                    )
                    
                    descriptors.append(discovered_descriptor)
                except ProtocolError as error:
                    logging.debug(f'cannot read {descriptor.handle:04X}:', error)
                except TimeoutError:
                    logging.debug('read timeout')
                    
                    
            current_characteristic.descriptors = descriptors
            characteristics.append(current_characteristic)
        
        service = Service(uuid=service.uuid.to_hex_str(), 
                characteristics=characteristics)
        services.append(service)

    logging.debug("Discovered everything")
    return services
