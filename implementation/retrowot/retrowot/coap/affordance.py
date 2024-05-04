import asyncio
import datetime
from aiocoap import *
from aiocoap import resource, CHANGED, CONTENT
from aiocoap.resource import ObservableResource, Site, Resource
from typing import Dict, Any, Callable

from configs import settings
from bluetooth.client import Client
from pyee import AsyncIOEventEmitter
from fastapi.encoders import jsonable_encoder
import json

client = Client()

class ThingDescriptonResource(Resource):
    
    def __init__(self, thing_description: str):
        super().__init__()
        self.content = thing_description
        
    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="A Thing Description")

    async def render_get(self, request):
        print("Resource requested")
        return Message(code=CONTENT, payload=self.content.encode())
    
class ObservableResource(ObservableResource):
    put_request: Callable = None
    content: Any = b""
    running_task: asyncio.Task = None

    def __init__(self, client, interaction):
        super().__init__()
        self.content = b"Initial state"
        interaction_parts = interaction.split("/")
        self._interaction_parts = interaction.split("/")
        self.device = self._interaction_parts[3]

        async def get_request():
            print("GET REQUEST")
            device = self.device
            service_uuid = self._interaction_parts[4].replace("urn:uuid:", "")
            characteristic_uuid = self._interaction_parts[5].replace("urn:uuid:", "")
            emitter = AsyncIOEventEmitter()

            emitter.on("read", lambda x: Message(code=CONTENT, payload=x))

            print(
                f"Device: {device}, Service: {service_uuid}, Characteristic: {characteristic_uuid}"
            )
            loop = asyncio.get_running_loop()  # Get the running loop
            task_2 = loop.create_task(
                client.read_value(
                    connection_address=device,
                    service_uuid=service_uuid,
                    characteristic_uuid=characteristic_uuid,
                    emitter=emitter,
                )
            )
            result = await task_2
            self.content = result
            return Message(code=CONTENT, payload=result)

        self.get_request = get_request
        
        async def put_request():
            print("GET REQUEST")
            interaction_parts = interaction.split("/")
            device = self.device
            service_uuid = self._interaction_parts[4].replace("urn:uuid:", "")
            characteristic_uuid = self._interaction_parts[5].replace("urn:uuid:", "")
            emitter = AsyncIOEventEmitter()

            def update_content(value):
                print(f"New Value: {value}")
                self.content = value
                self.updated_state(Message(code=CHANGED, payload=value))

            emitter.on("notify", lambda x: update_content(x.value))
            print(
                f"Device: {device}, Service: {service_uuid}, Characteristic: {characteristic_uuid}"
            )
            loop = asyncio.get_running_loop()  # Get the running loop
            task_2 = loop.create_task(
                client.notify(
                    connection_address=device,
                    service_uuid=service_uuid,
                    characteristic_uuid=characteristic_uuid,
                    emitter=emitter,
                )
            )

            self.running_task = task_2
            #await task_2

        self.put_request = put_request

        print("Created ObservableResource")
        print("Observaitions: ", self._observations)
        
    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="A Observable Resource")
    
    async def render_get(self, request):
        print(request)
        print("Resource requested")
        if request.opt.observe == 0:
            print("Starting observation")
            await self.put_request()
        elif request.opt.observe == 1:
            print("Stopping observation")
            self.running_task.cancel()
        else:
            await self.get_request()
        return Message(payload=self.content)

    async def render_put(self, request):
        self.content = request.payload
        print("Resource updated")
        await self.put_request()
        return Message(code=CHANGED, payload=self.content)


class ReadResource(Resource):
    get_request: Callable = None

    def __init__(self, client, interaction):
        super().__init__()
        self.content = b"Initial state"
        interaction_parts = interaction.split("/")
        self._interaction_parts = interaction.split("/")
        self.device = self._interaction_parts[3]

        async def get_request():
            print("GET REQUEST")
            interaction_parts = interaction.split("/")
            device = self.device
            service_uuid = self._interaction_parts[4].replace("urn:uuid:", "")
            characteristic_uuid = self._interaction_parts[5].replace("urn:uuid:", "")
            emitter = AsyncIOEventEmitter()

            emitter.on("read", lambda x: Message(code=CONTENT, payload=x))

            print(
                f"Device: {device}, Service: {service_uuid}, Characteristic: {characteristic_uuid}"
            )
            loop = asyncio.get_running_loop()  # Get the running loop
            task_2 = loop.create_task(
                client.read_value(
                    connection_address=device,
                    service_uuid=service_uuid,
                    characteristic_uuid=characteristic_uuid,
                    emitter=emitter,
                )
            )
            result = await task_2
            print(result)
            return Message(code=CONTENT, payload=result)

        self.get_request = get_request

        print("Created ReadResource")
    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="A Readable Resource")
    
    async def render_get(self, request):
        print("Resource requested")
        return await self.get_request()


class WriteResource(Resource):
    post_request: Callable = None

    def __init__(self, client, interaction):
        super().__init__()
        self.content = b"Initial state"

        async def post_request(value: Any):
            print("GET REQUEST")
            interaction_parts = interaction.split("/")
            device = interaction_parts[0]
            service_uuid = interaction_parts[1].replace("urn:uuid:", "")
            characteristic_uuid = interaction_parts[2].replace("urn:uuid:", "")
            emitter = AsyncIOEventEmitter()

            emitter.on("write", lambda x: Message(code=CONTENT, payload=b"204"))
            print(
                f"Device: {device}, Service: {service_uuid}, Characteristic: {characteristic_uuid}"
            )
            loop = asyncio.get_running_loop()
            task_2 = loop.create_task(
                client.write_value(
                    value=value,
                    connection_address=device,
                    service_uuid=service_uuid,
                    characteristic_uuid=characteristic_uuid,
                    emitter=emitter,
                )
            )
            await task_2

        self.post_request = post_request
        print("Created WriteResource")
        
    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="A Writable Resource")
    
    async def render_put(self, request):
        self.content = request.payload
        print("Resource updated")
        await self.post_request(self.content)
        self.updated_state(
            Message(code=CHANGED, payload=self.content)
        )  # Notify observers
        return Message(code=CHANGED, payload=self.content)


class ReadWriteResource(Resource):
    get_request: Callable = None
    post_request: Callable = None

    def __init__(self, client, interaction):
        super().__init__()
        self.content = b"Initial state"

        async def get_request():
            print("GET REQUEST")
            interaction_parts = interaction.split("/")
            device = interaction_parts[0]
            service_uuid = interaction_parts[1].replace("urn:uuid:", "")
            characteristic_uuid = interaction_parts[2].replace("urn:uuid:", "")
            emitter = AsyncIOEventEmitter()

            emitter.on("read", lambda x: Message(code=CONTENT, payload=x))

            loop = asyncio.get_running_loop()  # Get the running loop
            task_2 = loop.create_task(
                client.read_value(
                    connection_address=device,
                    service_uuid=service_uuid,
                    characteristic_uuid=characteristic_uuid,
                    emitter=emitter,
                )
            )
            await task_2

        self.get_request = get_request

        async def post_request(value: Any):
            interaction_parts = interaction.split("/")
            device = interaction_parts[0]
            service_uuid = interaction_parts[1].replace("urn:uuid:", "")
            characteristic_uuid = interaction_parts[2].replace("urn:uuid:", "")
            emitter = AsyncIOEventEmitter()

            emitter.on("write", lambda x: Message(code=CONTENT, payload=b"204"))

            loop = asyncio.get_running_loop()
            task_2 = loop.create_task(
                client.write_value(
                    value=value,
                    connection_address=device,
                    service_uuid=service_uuid,
                    characteristic_uuid=characteristic_uuid,
                    emitter=emitter,
                )
            )
            await task_2

        self.post_request = post_request

        print("Created ReadWriteResource")

    async def render_get(self, request):
        print("Resource requested")
        return await self.get_request()
    
    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="A Read- and Writable Resource")
    
    async def render_put(self, request):
        self.content = request.payload
        print("Resource updated")

        await self.post_request(self.content)
        self.updated_state(
            Message(code=CHANGED, payload=self.content)
        )  # Notify observers
        return Message(code=CHANGED, payload=self.content)


async def generate_subsite(device, site, subsites: Dict):
    global client
    if not client.is_initalized():
        await client.initalize(
            hci_device_name=settings.hci.name,
            hci_device_link=settings.hci.link,
            hci_device_mac=settings.hci.mac,
        )

    thing_description = device.thing_description
    deviceAddress = device.address.uuid
    td = json.dumps(jsonable_encoder(thing_description.dict()))
    print("Generating subsite for device: " + str(deviceAddress))

    thingdescription_site = Site()

    thingdescription_site.add_resource([], ThingDescriptonResource(td))

    print(thing_description)
    for property_affordance in thing_description.properties:
        print(property_affordance)
        for form in property_affordance.forms:

            if form.href.startswith("coap://"):
                href = form.href.split("/")[4:]
                if "readproperty" in form.op:
                    resource = ReadResource(client, form.href)
                elif "writeproperty" in form.op:
                    resource = WriteResource(client, form.href)
                elif "readwrite" in form.op:
                    resource = ReadWriteResource(client, form.href)
                else:
                    continue
                print(
                    "Affordance_subsite: "
                    + str(href)
                )
                thingdescription_site.add_resource(
                    href, resource
                )
                print("Added resource at: " + str([href]))

    for event_affordance in thing_description.events:
        for form in event_affordance.forms:
            
            if form.href.startswith("coap://"):
                href = form.href.split("/")[4:]
                resource = ObservableResource(client, form.href)

                thingdescription_site.add_resource(
                    href, resource
                )
                print("Added resource at: " + str([href]))

    for action_affordance in thing_description.actions:
        for form in action_affordance.forms:
            
            if form.href.startswith("coap://"):
                href = form.href.split("/")[4:]
                resource = WriteResource(client, form.href)

                thingdescription_site.add_resource(href, resource)
                print("Added resource at: " + str([href]))

    site.add_resource([deviceAddress], thingdescription_site)
