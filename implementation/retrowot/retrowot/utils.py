import os
from pyee import AsyncIOEventEmitter
from typing import Dict, Type

def normalize_bluetooth_uuid(uuid: str) -> str:
    """
    Normalize a Bluetooth UUID.

    Args:
        uuid (str): The UUID to be normalized.

    Returns:
        str: The normalized UUID.

    Example:
        >>> normalize_bluetooth_uuid("1234")
        '0000123400001000800000805F9B34FB'
        >>> normalize_bluetooth_uuid("56789ABC")
        '56789ABC00001000800000805F9B34FB'
    """
    if len(uuid) == 4:
        uuid = f"0000{uuid}00001000800000805F9B34FB"
    elif len(uuid) == 8:
        uuid = f"{uuid}00001000800000805F9B34FB"
    return uuid


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
        