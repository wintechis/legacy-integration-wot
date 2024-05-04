from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from bluetooth.discovery import device_discovery, service_discovery
from pyee import AsyncIOEventEmitter
from bluetooth.client import Client as BluetoothClient
from fastapi.encoders import jsonable_encoder

from zigbee.client import ZigbeeClient
from utils import Emitter
from configs import logger

mainRouter = APIRouter()
emitters = Emitter()


@mainRouter.get("/")
async def root():
    logger.debug("Client called root endpoint")
    return {"message": "Hello World"}


@mainRouter.get("/bluetooth_gatt/device_discovery")
async def device_discovery():
    logger.debug("Client called bluetooth device discovery endpoint")
    client = BluetoothClient()

    await client.service_discovery(5)

    logger.debug("Discovery Service found devices: {}".format(client.bluetooth_devices))
    return JSONResponse(
        content={"discovered_devices": list(client.bluetooth_devices.keys())},
        status_code=200,
    )


@mainRouter.get("/bluetooth_gatt/service_discovery/{payload}")
async def service_discovery(payload: str):
    logger.debug(
        f"Client called bluetooth service discovery endpoint with the data: {payload}"
    )
    client = BluetoothClient()

    device = client.get_device(payload)
    
    if device is None:
        await client.discover_device(payload)
        device = client.get_device(payload)
        
    if device is None:
        return Response(content="Device not found", status_code=404)
    if device.is_discovered():
        return JSONResponse(
            content={
                "discovered_services": [_ for _ in jsonable_encoder(device.services)]
            },
            status_code=200,
        )

    await client.device_discovery(payload)

    logger.debug("Emit services_discovered")
    emitters.device_discovery_emitter.emit("services_discovered", device)
    return JSONResponse(
        content={"discovered_services": [_ for _ in jsonable_encoder(device.services)]},
        status_code=200,
    )


@mainRouter.get("/zigbee/device_discovery")
async def device_discovery():
    logger.debug("Client called zigbee device discovery endpoint")
    client = ZigbeeClient()
    if not client.is_active:
        await client.start_zigbee(add_db=False)
        await client._info()
    devices = await client.device_discovery(15)

    print("device_discovery")
    return JSONResponse(content={"discovered_devices": devices}, status_code=200)


@mainRouter.get("/zigbee/service_discovery/{payload}")
async def service_discovery(payload: str):
    logger.debug(
        f"Client called zigbee service discovery endpoint with the data: {payload}"
    )
    client = ZigbeeClient()
    if not client.is_active:
        await client.start_zigbee(add_db=False)
        await client._info()

    device = client.get_device(payload)
    await client.service_discovery(device)
    rdf = device.to_rdf()
    rdf.serialize(
        destination="/home/rene/Repositories/PhD/retrowot/retrowot/zigbee.ttl",
        format="turtle",
    )
    rdf.serialize(
        destination="/home/rene/Repositories/PhD/retrowot/retrowot/zigbee_test_1_device.ttl",
        format="turtle",
    )

    logger.debug("Emit services_discovered")
    emitters.device_discovery_emitter.emit("services_discovered", device)

    if device is None:
        return Response(content="Device not found", status_code=404)
    if device.is_discovered():
        return JSONResponse(
            content={
                "discovered_services": [_ for _ in jsonable_encoder(device.endpoints)]
            },
            status_code=200,
        )

    await client.device_discovery(5)

    return JSONResponse(
        content={
            "discovered_services": [_ for _ in jsonable_encoder(device.endpoints)]
        },
        status_code=200,
    )
