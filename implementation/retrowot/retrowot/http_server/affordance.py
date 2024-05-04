from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
import asyncio
from pyee import AsyncIOEventEmitter
from bluetooth.client import Client
from zigbee.client import ZigbeeClient
from bluetooth.devices import BLEDevice as BluetoothDevice
from zigbee.device import ZigbeeDevice  
from typing import Any
import json
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE, HTTP_501_NOT_IMPLEMENTED
from configs import logger



def add_read_resource_endpoint(router: APIRouter, affordance, href, device) -> APIRouter:
    interaction_parts = href.split("/")
    endpoint = interaction_parts[4:]
    uri = f"/" + "/".join(endpoint)
    
    logger.debug("Generate new router for device with the following configuration: ")


    get_handler = ReadResource(affordance.title, href)
    print(type(device))
    if isinstance(device, BluetoothDevice):
        print("added bluetooth get")
        router.add_api_route(uri, get_handler.handle_bluetooth_get, methods=["get"])
    elif isinstance(device, ZigbeeDevice):
        print("added zigbee get")
        router.add_api_route(uri, get_handler.handle_zigbee_get, methods=["get"])
    return router


def add_write_resource_endpoint(router, affordance, href, device) -> APIRouter:
    interaction_parts = href.split("/")
    endpoint = interaction_parts[4:]
    uri = f"/" + "/".join(endpoint)

    logger.debug("Generate new router for device with the following configuration: ")


    get_handler = WriteResource(affordance.title, href)
    if isinstance(device, BluetoothDevice):
        print("added bluetooth post")
        router.add_api_route(uri, get_handler.handle_bluetooth_post, methods=["post"])
    elif isinstance(device, ZigbeeDevice):
        print("added zigbee post")
        router.add_api_route(uri, get_handler.handle_zigbee_post, methods=["post"])
    return router


def add_read_write_resource_endpoint(router, affordance, href, device) -> APIRouter:
    print("READ_WRITE_RESOURCE_ENDPOINT")
    pass


def add_event_resource_endpoint(router, affordance, href, device) -> APIRouter:
    interaction_parts = href.split("/")
    endpoint = interaction_parts[4:]
    uri = f"/" + "/".join(endpoint)
    get_handler = ReadResource(affordance.title, href)
    router.add_api_route(uri, get_handler.handle_bluetooth_get, methods=["get"])
    return router


def add_action_resource_endpoint(router, affordance, href, device) -> APIRouter:
    interaction_parts = href.split("/")
    endpoint = interaction_parts[4:]
    uri = f"/" + "/".join(endpoint)

    logger.debug("Generate new router for device with the following configuration: ")


    get_handler = ActionResource(affordance.title, href)
    if isinstance(device, BluetoothDevice):
        print("added bluetooth put")
        router.add_api_route(uri, get_handler.handle_bluetooth_post, methods=["put"])
    elif isinstance(device, ZigbeeDevice):
        print("added zigbee put")
        router.add_api_route(uri, get_handler.handle_zigbee_post, methods=["put"])
    return router


class ActionResource:
    def __init__(self, name: str, interaction: str) -> None:
        self.name = name
        self.client = Client()
        self.zigbee_client = ZigbeeClient()
        self._interaction_parts = interaction.split("/")
        self.device = self._interaction_parts[3]
        logger.debug(f"Resource-type: Action Resource")
        logger.debug(f"Affordance Name: {name}")
        logger.debug(f"Device Address: {self.device}")
        logger.debug(f"Affordance Link: {self._interaction_parts}")

        
    async def handle_zigbee_post(self):
        
        endpoint_uuid =self._interaction_parts[4]
        cluster_id = self._interaction_parts[5]
        command_id = self._interaction_parts[6]
        
        emitter = AsyncIOEventEmitter()
        
        
        
        print(f"zigbee post with: {self.device} {endpoint_uuid} {cluster_id} {command_id}")

        loop = asyncio.get_running_loop()

        task_2 = loop.create_task(
            self.zigbee_client.update_command(
                ieee=self.device,
                endpoint_id=endpoint_uuid,
                cluster_id=cluster_id,
                command_id=command_id
            )
        )

        await task_2

    async def handle_bluetooth_post(self, value: Any):
        return Response(status_code=HTTP_501_NOT_IMPLEMENTED)

class WriteResource:
    def __init__(self, name: str, interaction: str) -> None:
        self.name = name
        self.client = Client()
        self.zigbee_client = ZigbeeClient()
        self._interaction_parts = interaction.split("/")
        self.device = self._interaction_parts[3]
        logger.debug(f"Resource-type: Read Resource")
        logger.debug(f"Affordance Name: {name}")
        logger.debug(f"Device Address: {self.device}")
        logger.debug(f"Affordance Link: {self._interaction_parts}")

        
    async def handle_zigbee_post(self, value: Any):
        
        endpoint_uuid = self._interaction_parts[4]
        cluster_id = self._interaction_parts[5]
        attribute_id = self._interaction_parts[6]
        
        emitter = AsyncIOEventEmitter()
        
        
        emitter.on("write", lambda x: Response(x))

        loop = asyncio.get_running_loop()

        task_2 = loop.create_task(
            self.zigbee_client.write_attribute(
                value=value,
                ieee=self.device,
                endpoint_id=endpoint_uuid,
                cluster_id=cluster_id,
                attribute_id=attribute_id,
                emitter=emitter,
            )
        )

        await task_2

    async def handle_bluetooth_post(self, value: Any):
        print("POST REQUEST")

        # Check if the client is already connected to the device
        if self.client.has_active_connection(self.device):
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
            
            
        service_uuid = self._interaction_parts[4]
        characteristic_uuid = self._interaction_parts[5]

        emitter = AsyncIOEventEmitter()

        emitter.on("write", lambda x: Response(x))

        loop = asyncio.get_running_loop()

        task_2 = loop.create_task(
            self.client.write_value(
                value=value,
                connection_address=self.device,
                service_uuid=service_uuid,
                characteristic_uuid=characteristic_uuid,
                emitter=emitter,
            )
        )

        await task_2


class ReadResource:
    def __init__(self, name: str, interaction: str) -> None:
        self.name = name
        self.client = Client()
        interaction_parts = interaction.split("/")
        self.zigbee_client = ZigbeeClient()
        self._interaction_parts = interaction.split("/")
        self.device = self._interaction_parts[3]
        logger.debug(f"Resource-type: Read Resource")
        logger.debug(f"Affordance Name: {name}")
        logger.debug(f"Device Address: {self.device}")
        logger.debug(f"Affordance Link: {interaction_parts}")

            
    async def handle_zigbee_get(self):
        
        endpoint_uuid = self._interaction_parts[4]
        cluster_id = self._interaction_parts[5]
        attribute_id = self._interaction_parts[6]
        
        emitter = AsyncIOEventEmitter()
        
        
        emitter.on("read", lambda x: Response(x))

        loop = asyncio.get_running_loop()

        task_2 = loop.create_task(
            self.zigbee_client.read_attribute(
                ieee=self.device,
                endpoint_id=endpoint_uuid,
                cluster_id=cluster_id,
                attribute_id=attribute_id,
                emitter=emitter,
            )
        )

        await task_2
        
 
    
    async def handle_bluetooth_get(self):
        print("GET REQUEST")
        # Check if the client is already connected to the device
        if self.client.has_active_connection(self.device):
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

        service_uuid = self._interaction_parts[4]
        characteristic_uuid = self._interaction_parts[5]


        loop = asyncio.get_running_loop()  # Get the running loop
        task_2 = loop.create_task(
            self.client.read_value(
                connection_address=self.device,
                service_uuid=service_uuid,
                characteristic_uuid=characteristic_uuid,
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

import json
from decimal import Decimal
from fastapi.encoders import jsonable_encoder
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)



def generate_subsite(server, device, *args, **kwargs):
    device_name = device.thing_description._device_address

    thing_router = APIRouter(prefix=f"/{device_name}")

    def get_thing_description():
        thing_description = device.thing_description
        td = jsonable_encoder(thing_description.dict())
        return JSONResponse(content=td)
    
    def get_thing_model():
        thing_description = device.thing_description
        data = thing_description.dict()
        data['base'] = "gatt://{{MacOrWebBluetoothId}}/"
        tm = jsonable_encoder(data)
        td_dump = json.dumps(tm)
        title = thing_description.title.replace(":", "-")
        logger.debug(f"Title: {title}") 
        td_dump = td_dump.replace(f"gatt://{title}/", "./")
        td = json.loads(td_dump)
        
        return JSONResponse(content=td)  

    thing_router.add_api_route("/", get_thing_description, methods=["get"])

    thing_router.add_api_route("/tm/", get_thing_model, methods=["get"])
    
    for property_affordance in device.thing_description.properties:
        print(property_affordance)
        for form in property_affordance.forms:
            if "readproperty" in form.op:
                add_read_resource_endpoint(
                    thing_router, property_affordance, form.href, device
                )
            elif "writeproperty" in form.op:
                add_write_resource_endpoint(
                    thing_router, property_affordance, form.href, device
                )
            elif "readwrite" in form.op:
                add_read_write_resource_endpoint(
                    thing_router, property_affordance, form.href, device
                )
            else:
                continue
            

    for event_affordance in device.thing_description.events:
        for form in event_affordance.forms:
            add_event_resource_endpoint(thing_router, event_affordance, form.href, device)
      

    for action_affordance in device.thing_description.actions:
        logger.debug(f"Action Affordance: {action_affordance}")
        for form in action_affordance.forms:
            
            add_action_resource_endpoint(thing_router, action_affordance, form.href, device)
            
    server.include_router(thing_router)
    print("generate_subsite")
