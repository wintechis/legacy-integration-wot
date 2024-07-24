import asyncio
import json
from decimal import Decimal
from typing import Any, Union

from base_models import Device
from bluetooth.client import Client
from bluetooth.devices import BLEDevice as BluetoothDevice
from configs import logger
from fastapi import APIRouter, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pyee import AsyncIOEventEmitter
from starlette.status import HTTP_501_NOT_IMPLEMENTED, HTTP_503_SERVICE_UNAVAILABLE
from thing_description.models import Form, InteractionAffordance, ThingDescription
from zigbee.client import ZigbeeClient
from zigbee.device import ZigbeeDevice


class InteractionPattern:
    device_address: str


class BluetoothGATTInteractionPattern(InteractionPattern):

    service_uuid: str
    characteristic_uuid: str

    def __init__(self, base: str, interaction: str):
        interaction_parts = interaction.split("/")
        self.device_address = base.lstrip("gatt://")
        self.service_uuid = interaction_parts[1]
        self.characteristic_uuid = interaction_parts[2]


class ZigBeeInteractionPattern(InteractionPattern):
    endpoint_id: str
    cluster_id: str
    attribute_id: str

    def __init__(self, base: str, interaction: str):
        interaction_parts = interaction.split("/")
        self.device_address = base.lstrip("zigbee://")
        self.endpoint_id = interaction_parts[1]
        self.cluster_id = interaction_parts[2]
        self.attribute_id = interaction_parts[3]


def add_read_resource_endpoint(
    router: APIRouter, affordance: InteractionAffordance, form: Form, device: Device
) -> APIRouter:

    logger.debug("Generate new router for device with the following configuration: ")

    get_handler = ReadResource(affordance.title, form.href, device.thing_description)
    path = form.href.lstrip(".")
    if isinstance(device, BluetoothDevice):
        print("added bluetooth get")
        router.add_api_route(path, get_handler.handle_bluetooth_get, methods=["get"])
    elif isinstance(device, ZigbeeDevice):
        print("added zigbee get")
        router.add_api_route(path, get_handler.handle_zigbee_get, methods=["get"])
    print(f"Added read resource endpoint: {device.thing_description.baseUri}/{path}")

    with open("./notes.txt", "a") as f:
        f.write("generate_subsite\n")
        f.write(f"read endpoint: {path}\n")
    return router


def add_write_resource_endpoint(
    router: APIRouter, affordance: InteractionAffordance, form: Form, device: Device
) -> APIRouter:
    path = form.href.lstrip(".")
    logger.debug("Generate new router for device with the following configuration: ")

    get_handler = WriteResource(affordance.title, form.href, device.thing_description)
    if isinstance(device, BluetoothDevice):
        print("added bluetooth post")
        router.add_api_route(path, get_handler.handle_bluetooth_post, methods=["post"])
    elif isinstance(device, ZigbeeDevice):
        print("added zigbee post")
        router.add_api_route(path, get_handler.handle_zigbee_post, methods=["post"])

    with open("./notes.txt", "a") as f:
        f.write("generate_subsite\n")
        f.write(f"write endpoint: {path}\n")
    return router


def add_read_write_resource_endpoint(
    router: APIRouter, affordance: InteractionAffordance, form: Form, device: Device
) -> APIRouter:
    print("READ_WRITE_RESOURCE_ENDPOINT")
    pass


def add_event_resource_endpoint(
    router: APIRouter, affordance: InteractionAffordance, form: Form, device: Device
) -> APIRouter:
    path = form.href.lstrip(".")
    get_handler = ReadResource(affordance.title, form.href, device.thing_description)
    router.add_api_route(path, get_handler.handle_bluetooth_get, methods=["get"])
    with open("./notes.txt", "a") as f:
        f.write("generate_subsite\n")
        f.write(f"event endpoint: {path}\n")
    return router


def add_action_resource_endpoint(
    router: APIRouter, affordance: InteractionAffordance, form: Form, device: Device
) -> APIRouter:
    path = form.href.lstrip(".")
    logger.debug("Generate new router for device with the following configuration: ")
    print("ACTION_RESOURCE_ENDPOINT:", path)
    get_handler = ActionResource(affordance.title, form.href, device.thing_description)
    if isinstance(device, BluetoothDevice):
        print("added bluetooth put")
        router.add_api_route(path, get_handler.handle_bluetooth_post, methods=["put"])
    elif isinstance(device, ZigbeeDevice):
        print("added zigbee put")
        router.add_api_route(path, get_handler.handle_zigbee_post, methods=["put"])

    with open("./notes.txt", "a") as f:
        f.write("generate_subsite\n")
        f.write(f"action endpoint: {path}\n")
    return router


class ActionResource:
    def __init__(self, name: str, interaction: str, thing_description) -> None:
        if thing_description.baseUri.startswith("zigbee"):
            self.client = ZigbeeClient()
            self.interactionPattern = ZigBeeInteractionPattern(
                thing_description.baseUri, interaction
            )
        elif thing_description.baseUri.startswith("gatt"):
            self.client = Client()
            self.interactionPattern = BluetoothGATTInteractionPattern(
                thing_description.baseUri, interaction
            )

    async def handle_zigbee_post(self):

        emitter = AsyncIOEventEmitter()

        loop = asyncio.get_running_loop()

        task_2 = loop.create_task(
            self.client.update_command(
                ieee=self.interactionPattern.device_address,
                endpoint_id=self.interactionPattern.endpoint_id,
                cluster_id=self.interactionPattern.cluster_id,
                command_id=self.interactionPattern.command_id,
            )
        )

        await task_2

    async def handle_bluetooth_post(self, value: Any):

        # Check if the client is already connected to the device
        if self.client.has_active_connection(self.interactionPattern.device_address):
            headers = {"Retry-After": "0.1"}  # Retry after 0.1 seconds
            content = {
                "message": "Service temporarily unavailable. Please retry after 0.1 seconds."
            }
            print("Already active connection")
            return JSONResponse(
                content=content,
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                headers=headers,
            )

        emitter = AsyncIOEventEmitter()

        emitter.on("write", lambda x: Response(x))

        loop = asyncio.get_running_loop()

        task_2 = loop.create_task(
            self.client.write_value(
                value=value,
                connection_address=self.interactionPattern.device_address,
                service_uuid=self.interactionPattern.service_uuid,
                characteristic_uuid=self.interactionPattern.characteristic_uuid,
                emitter=emitter,
            )
        )

        await task_2


class WriteResource:
    def __init__(
        self, name: str, interaction: str, thing_description: ThingDescription
    ) -> None:
        if thing_description.baseUri.startswith("zigbee"):
            self.client = ZigbeeClient()
            self.interactionPattern = ZigBeeInteractionPattern(
                thing_description.baseUri, interaction
            )
        elif thing_description.baseUri.startswith("gatt"):
            self.client = Client()
            self.interactionPattern = BluetoothGATTInteractionPattern(
                thing_description.baseUri, interaction
            )

    async def handle_zigbee_post(self, value: Any):

        emitter = AsyncIOEventEmitter()

        emitter.on("write", lambda x: Response(x))

        loop = asyncio.get_running_loop()

        task_2 = loop.create_task(
            self.client.write_attribute(
                value=value,
                ieee=self.interactionPattern.device_address,
                endpoint_id=self.interactionPattern.endpoint_id,
                cluster_id=self.interactionPattern.cluster_id,
                attribute_id=self.interactionPattern.attribute_id,
                emitter=emitter,
            )
        )

        await task_2

    async def handle_bluetooth_post(self, value: Any):
        print("POST REQUEST")

        # Check if the client is already connected to the device
        if self.client.has_active_connection(self.interactionPattern.device_address):
            headers = {"Retry-After": "0.1"}  # Retry after 0.1 seconds
            content = {
                "message": "Service temporarily unavailable. Please retry after 0.1 seconds."
            }
            print("Already active connection")
            return JSONResponse(
                content=content,
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                headers=headers,
            )

        emitter = AsyncIOEventEmitter()

        emitter.on("write", lambda x: Response(x))

        loop = asyncio.get_running_loop()

        task_2 = loop.create_task(
            self.client.write_value(
                value=value,
                connection_address=self.interactionPattern.device_address,
                service_uuid=self.interactionPattern.service_uuid,
                characteristic_uuid=self.interactionPattern.characteristic_uuid,
                emitter=emitter,
            )
        )

        await task_2


class ReadResource:
    client: Union[ZigbeeClient, Client]
    interactionPattern: Union[ZigBeeInteractionPattern, BluetoothGATTInteractionPattern]

    def __init__(
        self, name: str, interaction: str, thing_description: ThingDescription
    ) -> None:
        if thing_description.baseUri.startswith("zigbee"):
            self.client = ZigbeeClient()
            self.interactionPattern = ZigBeeInteractionPattern(
                thing_description.baseUri, interaction
            )
        elif thing_description.baseUri.startswith("gatt"):
            self.client = Client()
            self.interactionPattern = BluetoothGATTInteractionPattern(
                thing_description.baseUri, interaction
            )

        logger.debug(f"Resource-type: Read Resource")

    async def handle_zigbee_get(self):

        emitter = AsyncIOEventEmitter()

        emitter.on("read", lambda x: Response(x))

        loop = asyncio.get_running_loop()

        task_2 = loop.create_task(
            self.client.read_attribute(
                ieee=self.interactionPattern.device_address,
                endpoint_id=self.interactionPattern.endpoint_id,
                cluster_id=self.interactionPattern.cluster_id,
                attribute_id=self.interactionPattern.attribute_id,
                emitter=emitter,
            )
        )

        await task_2

    async def handle_bluetooth_get(self):
        print("GET REQUEST")
        print(self.interactionPattern.device_address)
        print(self.interactionPattern.service_uuid)
        print(self.interactionPattern.characteristic_uuid)

        # Check if the client is already connected to the device
        if self.client.has_active_connection(self.interactionPattern.device_address):
            headers = {"Retry-After": "0.1"}  # Retry after 0.1 seconds
            content = {
                "message": "Service temporarily unavailable. Please retry after 0.1 seconds."
            }
            print("Already active connection")
            return JSONResponse(
                content=content,
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                headers=headers,
            )

        emitter = AsyncIOEventEmitter()

        emitter.on("read", lambda x: Response(x))

        loop = asyncio.get_running_loop()  # Get the running loop
        task_2 = loop.create_task(
            self.client.read_value(
                connection_address=self.interactionPattern.device_address,
                service_uuid=self.interactionPattern.service_uuid,
                characteristic_uuid=self.interactionPattern.characteristic_uuid,
                emitter=emitter,
            )
        )

        await task_2

        print(task_2.result())
        return Response(task_2.result())


def add_endpoint(router, device, href):
    router.add_api_route(
        href, lambda x: Response(device.thing_description), methods=["get"]
    )


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def generate_subsite(server, device: Device, *args, **kwargs):
    thing_description: ThingDescription = device.thing_description
    device_name = thing_description.title
    print(device_name)

    thing_router = APIRouter(prefix=f"/{device_name}")

    def get_thing_description():
        td = jsonable_encoder(thing_description.to_dict())
        return JSONResponse(content=td)

    def get_thing_model():
        data = thing_description.to_dict()
        data["baseUri"] = "gatt://{{MacOrWebBluetoothId}}/"
        tm = jsonable_encoder(data)
        td_dump = json.dumps(tm)
        title = thing_description.title.replace(":", "-")
        logger.debug(f"Title: {title}")
        td_dump = td_dump.replace(f"gatt://{title}/", "./")
        td = json.loads(td_dump)

        return JSONResponse(content=td)

    thing_router.add_api_route("/", get_thing_description, methods=["get"])

    thing_router.add_api_route("/tm/", get_thing_model, methods=["get"])

    with open("./notes.txt", "a") as f:
        f.write("generate_subsite\n")
        f.write(f"router_prefix: {thing_router.prefix}\n")

    for property_affordance in thing_description.properties:

        for form in property_affordance.forms:
            if "readproperty" in form.operation:
                add_read_resource_endpoint(
                    thing_router, property_affordance, form, device
                )
            elif "writeproperty" in form.operation:
                add_write_resource_endpoint(
                    thing_router, property_affordance, form, device
                )
            elif "readwrite" in form.operation:
                add_read_write_resource_endpoint(
                    thing_router, property_affordance, form, device
                )
            else:
                continue

    for event_affordance in device.thing_description.events:
        for form in event_affordance.forms:
            add_event_resource_endpoint(thing_router, event_affordance, form, device)

    for action_affordance in device.thing_description.actions:
        logger.debug(f"Action Affordance: {action_affordance}")
        for form in action_affordance.forms:

            add_action_resource_endpoint(thing_router, action_affordance, form, device)

    server.include_router(thing_router)
    print("generate_subsite")
