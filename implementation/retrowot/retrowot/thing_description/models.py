import json
from copy import deepcopy
from enum import Enum
from typing import Dict, List, Optional

import aiohttp
from configs import logger, settings
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Extra, Field
from rdflib import Graph, URIRef
from thing_description.queries import form_query
from thing_description.utils import (
    camel_case,
    process_parameters,
    query_result_to_dict,
    update_parameters,
)


class OperationType(str, Enum):
    READ_PROPERTY = "readproperty"
    WRITE_PROPERTY = "writeproperty"
    INVOKE_ACTION = "invokeaction"
    SUBSCRIBE_EVENT = "subscribeevent"
    UNSUBSCRIBE_EVENT = "unsubscribeevent"


class InteractionAffordanceType(str, Enum):
    PROPERTY_AFFORDANCE = "PropertyAffordance"
    ACTION_AFFORDANCE = "ActionAffordance"
    EVENT_AFFORDANCE = "EventAffordance"


def update_operation_type(operation: str) -> str:
    operation = operation.lower()
    if "readproperty" in operation:
        return OperationType.READ_PROPERTY
    elif "writeproperty" in operation:
        return OperationType.WRITE_PROPERTY
    elif "invokeaction" in operation:
        return OperationType.INVOKE_ACTION
    elif "subscribeevent" in operation:
        return OperationType.SUBSCRIBE_EVENT
    elif "unsubscribeevent" in operation:
        return OperationType.UNSUBSCRIBE_EVENT
    else:
        return operation


class Form(BaseModel):
    contentType: str = Field(serialization_alias="contentType")
    href: str = Field(serialization_alias="href")
    operation: str = Field(serialization_alias="op")
    parameters: Dict[str, str] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        self.operation = update_operation_type(self.operation)
        self.parameters = process_parameters(self)
        self.href = data["href"]

    def to_dict(self, parameters: dict) -> Dict[str, str]:
        form = deepcopy(self)
        form.__dict__.update(parameters)
        return form.model_dump(exclude={"parameters"})


class InteractionAffordance(BaseModel):
    title: str = Field(
        serialization_alias="title", default="TODO My Test Affordance Name"
    )
    description: Optional[str] = Field(serialization_alias="description", default="")
    returnType: str = Field(serialization_alias="type")
    form: str
    formInstantiation: Optional[Form] = None
    forms: List[Form] = []
    graph: Graph
    parameters: Dict[str, str] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"

    def __init__(self, **data):

        super().__init__(**data)

        if data["form"] != None:
            query_results = data["graph"].query(
                form_query, initBindings={"form": URIRef(data["form"])}
            )
            query_data = query_result_to_dict(query_results)
            if len(query_data) > 0:
                # Here is the assumption that only one interactionAffordance is returned
                self.formInstantiation = Form(**query_data[0], graph=data["graph"], href=data["href"])
                self.forms.append(self.formInstantiation)
        self.parameters = process_parameters(self)

    def to_dict(self, instance_parameters: dict) -> Dict[str, str]:
        # Create a thing description based on the data in the model
        parameters = deepcopy(self.parameters)
        parameters = update_parameters(parameters, instance_parameters)

        thing_model = deepcopy(self)
        thing_model.__dict__.update(parameters)

        affordance_as_dict = thing_model.model_dump(
            exclude={"graph", "parameters", "form", "formInstantiation"}, by_alias=True
        )

        if thing_model.description == None:
            affordance_as_dict.pop("description")

        affordance_as_dict["forms"] = [
            self.formInstantiation.model_dump(
                exclude={"graph", "parameters"}, by_alias=True
            )
        ]

        return affordance_as_dict


class PropertyAffordance(InteractionAffordance):
    readOnly: bool = Field(
        description="True if the property is read-only", default=False
    )
    writeOnly: bool = Field(
        description="True if the property is write-only", default=False
    )
    observable: bool = Field(
        description="True if the property is observable", default=False
    )


class ActionAffordance(InteractionAffordance):
    input: Optional[any] = Field(description="The input of the action", default=None)
    output: Optional[any] = Field(description="The output of the action", default=None)
    safe: bool = Field(description="True if the action is safe", default=False)
    idempotent: bool = Field(
        description="True if the action is idempotent", default=False
    )
    synchronous: bool = Field(
        description="True if the action is synchronous", default=False
    )


class EventAffordance(InteractionAffordance):
    subscription: Optional[any] = Field(
        description="The subscription of the event", default=None
    )
    dataResponse: Optional[any] = Field(
        description="The data response of the event", default=None
    )
    cancellation: Optional[any] = Field(
        description="The cancellation of the event", default=None
    )


class ThingDescription(BaseModel):
    baseUri: str = Field(description="The base URI of the thing")
    title: str = Field(description="The title of the thing")
    properties: List[InteractionAffordance] = Field(
        [], description="The property affordances of the thing"
    )
    actions: List[InteractionAffordance] = Field(
        [], description="The actions of the thing"
    )
    events: List[InteractionAffordance] = Field(
        [], description="The events of the thing"
    )
    tms: List[str] = Field(
        [], description="The thing model", serialization_alias="links"
    )

    def to_dict(self) -> Dict[str, str]:
        td_as_dict = self.model_dump(exclude={"tms"})
        td_as_dict["@context"] = [
            "https://www.w3.org/2022/wot/td/v1.1",
            {
                "tm": "https://www.w3.org/2019/wot/tm#",
            },
        ]
        td_as_dict["@type"] = "td:Thing"
        if len(self.tms) > 0:
            td_as_dict["links"] = [
                {
                    "rel": "type",
                    "href": _,
                    "type": "application/tm+json",
                }
                for _ in self.tms
            ]

        td_as_dict["securityDefinitions"] = {"nosec_sc": {"scheme": "nosec"}}
        td_as_dict["security"] = ["nosec_sc"]
        # interactionAffordanceInstantiation
        if len(self.properties) > 0:
            td_as_dict["properties"] = {
                camel_case(_.title): _.to_dict({}) for _ in self.properties
            }
        else:
            td_as_dict["properties"] = {}

        if len(self.actions) > 0:
            td_as_dict["actions"] = {
                camel_case(_.title): _.to_dict({}) for _ in self.actions
            }
        else:
            td_as_dict["actions"] = {}

        if len(self.events) > 0:
            td_as_dict["events"] = {
                camel_case(_.title): _.to_dict({}) for _ in self.events
            }
        else:
            td_as_dict["events"] = {}

        return td_as_dict

    def to_json_ld(self) -> str:
        data = self.to_dict()
        return json.dumps(data, indent=4)

    async def publish_thing_description(self):
        """
        Publishes the thing description to the thing directory.

        Returns:
            A string representing the response from the thing directory.
        """

        async def _post(session, url, data):
            async with session.post(url, data=data) as response:
                return await response.text()

        file = jsonable_encoder(self.to_dict())

        async with aiohttp.ClientSession() as session:
            text = await _post(
                session=session,
                url=f"{settings.thing_directory.url}/{settings.thing_directory.post_endpoint}",
                data=json.dumps(file),
            )

            logger.debug(f"Response from thing directory: {text}")
