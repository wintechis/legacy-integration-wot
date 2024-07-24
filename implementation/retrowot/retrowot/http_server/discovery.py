from bluetooth.client import Client as BluetoothClient
from configs import logger
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse, Response
from utils import Emitter
from zigbee.client import ZigbeeClient

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

    # ToDo: Change name to service discovery
    await client.device_discovery(5)

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
        return RedirectResponse(f"/{device.thing_description.title}")

    # ToDo: Change name to service discovery
    await client.service_discovery(payload)

    logger.debug("Emit services_discovered")
    emitters.device_discovery_emitter.emit("services_discovered", device)

    return RedirectResponse(f"/{device.thing_description.title}")


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

    logger.debug("Emit services_discovered")
    emitters.device_discovery_emitter.emit("services_discovered", device)

    if device is None:
        return Response(content="Device not found", status_code=404)
    if device.is_discovered():
        return RedirectResponse(f"/{device.thing_description.title}")

    await client.device_discovery(5)

    # Redirect to TD
    return RedirectResponse(f"/{device.thing_description.title}")
