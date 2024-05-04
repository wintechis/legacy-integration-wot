import os
from pyee import AsyncIOEventEmitter
from typing import Dict, Type

    
def get_project_root() -> str:
    """Returns project root folder."""
    return os.path.dirname(os.path.abspath(__file__))

def get_file_path(file_name: str) -> str:
    """Returns file path."""
    file_location = get_file_location(file_name)
    return os.path.join(get_project_root(), file_location(file_name), file_name)

def get_file_location(file_name: str) -> str:
    """Returns file location."""
    return os.path.dirname(get_file_path(file_name))

class SingletonMeta(type):
    _instances: Dict[Type, 'SingletonMeta'] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
class Emitter(metaclass=SingletonMeta):
    device_discovery_emitter: AsyncIOEventEmitter = None
    device_affordance_emitters: AsyncIOEventEmitter = None
    
    def __init__(self):
        self.device_discovery_emitter = AsyncIOEventEmitter()
        self.device_affordance_emitters = AsyncIOEventEmitter()
        