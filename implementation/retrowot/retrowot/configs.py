import logging
import logging.config
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, EnvSettingsSource, SettingsConfigDict

load_dotenv()


import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def get_logger() -> logging.Logger:
    print(PROJECT_ROOT)
    logging.config.fileConfig(PROJECT_ROOT + "/retrowot/logging.conf")

    # Now you can get your logger and use it
    logger = logging.getLogger("RetroWoT")

    # Load the logging configuration

    return logger


logger = get_logger()


class HTTPConfig(BaseSettings):
    host: str = Field(default="", alias="HTTP_SERVER_HOST")
    port: int = Field(default=8000, alias="HTTP_SERVER_PORT")

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class CoAPConfig(BaseSettings):
    host: str = Field(default="", alias="COAP_SERVER_HOST")
    port: int = Field(default=5683, alias="COAP_SERVER_PORT")

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class BluetoothConfig(BaseSettings):
    device_discovery_timeout: int = Field(
        default=10, alias="BLUETOOTH_DEVICE_DISCOVERY_TIMEOUT"
    )

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class ThingDirectoryConfig(BaseSettings):
    url: str = Field(default="", alias="THING_DIRECTORY_URL")
    post_endpoint: str = Field(default="", alias="THING_DIRECTORY_ENDPOINT")
    use_thing_directory: bool = Field(default=False, alias="THING_DIRECTORY_ENABLED")

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class EnrichmentConfig(BaseSettings):
    enrichment_endpoint: str = Field(default="", alias="enrichment_endpoint")
    use_enrichment: bool = Field(default=False, alias="ENRICHMENT_ENABLED")
    use_service_enrichment: bool = Field(
        default=False, alias="ENRICHMENT_THROUGH_SERVICE_ENRICHMENT"
    )
    use_service_discovery: bool = Field(
        default=False, alias="ENRICHMENT_THROUGH_SERVICE_DISCOVERY"
    )
    middleware_interface: bool = Field(
        default=True, alias="CREATE_MIDDLEWARE_PROTOCOL_MEDIATOR"
    )
    use_primary_interface: bool = Field(default=True, alias="USE_PRIMARY_PROTOCOL")

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class ZigbeeConfig(BaseSettings):
    database: str = Field(default="/home/zigbee.db", alias="ZIGBEE_DATABASE")
    network_channel: int = Field(default=20, alias="ZIGBEE_NETWORK_CHANNEL")
    pairing_timeout: int = Field(default=60, alias="ZGIBEE_PAIRING_TIMEOUT")
    device_path: str = Field(default="/dev/ttyUSB0", alias="ZIGBEE_DEVICE_PATH")
    baurate: int = Field(default=115200, alias="ZIGBEE_DEVICE_BAURATE")
    radio_type: str = Field(default="ezsp", alias="ZIGBEE_DEVICE_RADIO_TYPE")

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class HCIConfig(BaseSettings):
    link: str = Field(default="test", alias="BLUETOOTH_HCI_DEVICE_LINK")
    mac: str = Field(default="F0:F1:F2:F3:F4:F5", alias="BLUETOOTH_HCI_DEVICE_MAC")
    name: str = Field(default="usb:01", alias="BLUETOOTH_HCI_DEVICE_NAME")

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class Settings(BaseSettings):

    hci: HCIConfig = Field(default_factory=HCIConfig)
    bluetooth: BluetoothConfig = Field(default_factory=BluetoothConfig)
    thing_directory: ThingDirectoryConfig = Field(default_factory=ThingDirectoryConfig)
    server_type: str = Field(default="coap", alias="SERVER_TYPE")
    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )
    http_server: HTTPConfig = Field(default_factory=HTTPConfig)
    coap_server: CoAPConfig = Field(default_factory=CoAPConfig)
    zigbee: ZigbeeConfig = Field(default_factory=ZigbeeConfig)
    enrichment: EnrichmentConfig = Field(default_factory=EnrichmentConfig)


settings = Settings()
logger.debug(f"Initialized settings with: {settings}")


if __name__ == "__main__":
    settings = Settings()
    print(settings)
