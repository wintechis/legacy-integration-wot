from aiocoap import CONTENT
from aiocoap.resource import Resource
from pyee import AsyncIOEventEmitter
from retrowot.bluetooth.client import Client
from bson import BSON
from typing import Dict, Any

class DiscoverDeviceResource(Resource):
    
   
    queue: dict = {}
    client: Client = None
    
    def __init__(self, devices: Dict):
        super().__init__()
        self.content = b"Initial state"
        self.queue = devices
        self.client = Client()
        

    async def render_get(self, request):
        data = {'discovered_devices': list(self.queue.keys())}
        print("Resource requested")
        bson_data = BSON.encode(data)
        return Message(code=CONTENT, payload=bson_data)
    
    async def render_post(self, request):
        # Extract the payload from the request
        payload = request.payload
        print(f"Received POST request with payload: {payload.decode()}")
        await self.client.service_discovery(5)
        # You can process the payload here and perform actions based on it

        # Sending a response (optional)
        response_payload = b"POST request received"
        return Message(code=CONTENT, payload=response_payload)
    
    
class DiscoverServiceResource(Resource):
    
    emitter: AsyncIOEventEmitter = None
    queue: dict = {}
    discovered_devices: dict = {}
    client: Client = None
    
    def __init__(self, devices: Dict, emitter: AsyncIOEventEmitter):
        super().__init__()
        self.content = b"Initial state"
        self.queue = devices
        self.emitter = emitter
        self.client = Client()

    
    async def render_post(self, request):
        # Extract the payload from the request
        payload = request.payload.decode()
        print(f"Received POST request with payload: {payload}")
        
        device = self.client.get_device(payload)
        
        if device is None:
            return Message(code=CONTENT, payload=b"Device not found")
        
        #if device.is_discovered():
        #    return Message(code=CONTENT, payload=b"Device already discovered")
        
        device_address = payload
        #device = self.queue[device_address][0].device
        
        if not device.is_connectable():
            return Message(code=CONTENT, payload=b"Device not connectable")
        

        
        await self.client.device_discovery(device_address)
        # You can process the payload here and perform actions based on it



        
        self.emitter.emit("services_discovered", device)
        # Sending a response (optional)
        response_payload = b"POST request received"
        return Message(code=CONTENT, payload=response_payload)