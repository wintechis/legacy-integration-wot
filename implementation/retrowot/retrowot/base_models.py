from pydantic import BaseModel
from thing_description.models import ThingDescription

class Device(BaseModel):
    thing_description: ThingDescription
    