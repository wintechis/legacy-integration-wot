from rdflib import Graph

from typing import Any, Dict, Union
from configs import settings, Settings
import time



class Form:
    
 
    
    def __init__(self, href, op: str, byte_wise_interpretation, graph: Graph, device_type: Union[str, None] = None):
        self.href: str = href
        self.contentType: str = self._get_content_type(byte_wise_interpretation)
        self.contentFormat: Union[None, int] = None
        self.op: str = op
        self.methodName: str = ""
        self.subprotocol: str = ""
        self._additional_properties: Dict[str, Any] = {}
        uri_fragments = self.href.split("/")
        uri = self.href.replace("urn:uuid:", "")

        if device_type == "http://purl.org/serviceCapability#BluetoothLE":
            self._process_ble(uri, settings)    
        elif device_type == "http://purl.org/serviceCapability#Zigbee":
            print("Zigbee not implemented yet")
        elif device_type == "coap":
            self._process_coap(uri, settings)
        elif device_type == "http":
            self._process_http(uri, settings)
        elif device_type == None:
            print("No device type specified")
        else:
            print("Unknown device type with device_type name: " + device_type)

    def __eq__(self, __value: 'Form') -> bool:
        if self.href != __value.href:
            return False
        if self.contentType != __value.contentType:
            return False
        if self.contentFormat != __value.contentFormat:
            return False
        if self.op != __value.op:    
            return False
        return True
    
    def _map_device_id(self, device_id: str) -> str:
        return device_id.replace(":", "-").upper()
    
    def _map_ble_id(self, id: str) -> str:
        if len(id) == 32:
            id = id[0:8] + "-" + id[8:12] + "-" + id[12:16] + "-" + id[16:20] + "-" + id[20:32]
        id = id.lower()
        return id
        
    

    
    
    def _process_ble(self, uri: str, settings: Settings) -> None:
        
        if self.op == "http://purl.org/serviceCapability#WriteInteraction":
            self.op = "writeproperty"
            self._additional_properties["sbo:methodName"] = 'sbo:write-without-response'
        elif self.op == "http://purl.org/serviceCapability#ReadInteraction":
            self.op = "readproperty"
            self._additional_properties["sbo:methodName"] = 'sbo:read'
        elif self.op == "http://purl.org/serviceCapability#SubscriptionCommand":
            self.op = "subscribeevent"
            self._additional_properties["sbo:methodName"] = 'sbo:notify'
        elif self.op == "http://purl.org/serviceCapability#ActionInteraction":
            self.op = "invokeaction"
            self._additional_properties["sbo:methodName"] = 'sbo:write-without-response'
        self.contentType = "application/x.binary-data-stream"
            
        uri_fragments = uri.split("/")
        device = uri_fragments[0]
        service = uri_fragments[1]
        characteristic = uri_fragments[2]
        
        self.href = (
            "gatt://"
            + self._map_device_id(device)
            + "/"
            + self._map_ble_id(service)
            + "/"
            + self._map_ble_id(characteristic)
        )
            
            
    def _process_http(self, uri: str, settings: Settings) -> None:
        if self.op == "http://purl.org/serviceCapability#WriteInteraction":
            self.op = "writeproperty"
            self.methodName = "PUT"
        elif self.op == "http://purl.org/serviceCapability#ReadInteraction":
            self.op = "readproperty"
            self.methodName = "GET"
        elif self.op == "http://purl.org/serviceCapability#SubscriptionCommand":
            self.op = "subscribeevent"
            self.methodName = "GET"

        self.href = (
            "http://"
            + settings.http_server.host
            + ":"
            + str(settings.http_server.port)
            + "/"
            + uri
        )
        
    def _process_coap(self, uri: str, settings: Settings) -> None:
        if self.op == "http://purl.org/serviceCapability#WriteInteraction":
            self.op = "writeproperty"
            self.methodName = "PUT"
        elif self.op == "http://purl.org/serviceCapability#ReadInteraction":
            self.op = "readproperty"
            self.methodName = "GET"
        elif self.op == "http://purl.org/serviceCapability#SubscriptionCommand":
            self.op = "subscribeevent"
            self.methodName = "GET"
            self.subprotocol = "cov:observe"

        self.href = (
            "coap://"
            + settings.coap_server.host
            + ":"
            + str(settings.coap_server.port)
            + "/"
            + uri
        )
        self.contentFormat = 60
        
        
    def _get_content_type(self, bytewise: bool) -> str:
        
        res = "text/plain;charset=utf-8"
        
        if bytewise:
            res = "application/octet-stream"
        
        return res
    def dict(self, *args, **kwargs):
        model_dict = {
            "href": self.href,
            "contentType": self.contentType,
            "op": self.op,
        }
        if self.contentFormat is not None:
            model_dict["contentFormat"] = self.contentFormat    

        if settings.server_type == "coap":
            model_dict["cov:method"]: self.methodName

        if self.subprotocol != "":
            model_dict["subprotocol"] = self.subprotocol

        if self._additional_properties != {}:
            model_dict.update(self._additional_properties)
            
        return model_dict