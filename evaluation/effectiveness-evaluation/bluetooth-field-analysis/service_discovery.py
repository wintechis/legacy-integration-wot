#!/home/rene/.cache/pypoetry/virtualenvs/woble-system-RUdZ6xzC-py3.10/bin/python
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional

import schedule
from bluetooth.client import Client
from pydantic import BaseModel

client = Client()
path_to_devices = "/home/rene/Repositories/PhD/woble-system/woble-system/woble_system/experiments/devices.json"
path_to_experiment = (
    "/home/rene/Repositories/PhD/woble-system/woble-system/woble_system/experiments/"
)


class CharacteristicReport(BaseModel):
    uuid: str


class ServiceReport(BaseModel):
    uuid: str
    characteristics: List[CharacteristicReport] = []


class DeviceReport(BaseModel):
    address: str
    services: List[ServiceReport] = []


class Report(BaseModel):
    start_time: datetime = datetime.now()
    finish_time: Optional[datetime] = None

    devices: Dict[str, DeviceReport] = {}


async def discover():
    print("Discovering services...")
    await client.power_on()
    await client.service_discovery(2)

    with open(path_to_devices, "r") as f:
        devices = json.load(f)

    print("Services discovered!")
    report = Report()
    for device in client.bluetooth_devices.values():
        print("Device: ", device.address.uuid)
        if device.address.uuid not in devices:

            report.devices[device.address.uuid] = DeviceReport(
                address=device.address.uuid
            )
            try:
                await asyncio.wait_for(client.device_discovery(device.address.uuid), 10)
            except Exception as e:
                print("Error while discovering services: " + str(e))
                continue

            for service in device.services:
                service_report = ServiceReport(uuid=service.uuid)
                for characteristic in service.characteristics:
                    service_report.characteristics.append(
                        CharacteristicReport(uuid=characteristic.uuid)
                    )
                report.devices[device.address.uuid].services.append(service_report)

    report.finish_time = datetime.now()
    start_time = report.start_time.strftime("%Y%d%m-%H:%M:%S")
    end_time = report.finish_time.strftime("%Y%d%m-%H:%M:%S")
    with open(f"{path_to_experiment}/{start_time}-{end_time}report.json", "w") as f:
        f.write(report.model_dump_json())
    with open(path_to_devices, "w") as f:
        devices += list(client.bluetooth_devices.keys())
        devices = list(set(devices))
        f.write(json.dumps(devices))
    await client.power_off()


async def run_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


# Function to run the task
def job():
    asyncio.create_task(discover())


async def main():
    c = Client()
    await c.initalize(
        hci_device_link="usb:0a12:0001",
        hci_device_name="Bumble",
        hci_device_mac="F0:F1:F2:F3:F4:F5",
    )
    await discover()


if __name__ == "__main__":

    asyncio.run(main())
