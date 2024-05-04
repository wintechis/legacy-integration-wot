from pydantic import BaseModel

class DataPoint(BaseModel):
    value: bytes
    characteristic: str
    service: str
    connection_address: str
