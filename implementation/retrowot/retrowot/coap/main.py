import asyncio
import datetime
from functools import partial
from typing import Any, Dict

from aiocoap import *
from aiocoap import CONTENT
from aiocoap.resource import Resource, Site, WKCResource
from pyee import AsyncIOEventEmitter

from retrowot.bluetooth.client import Client
from retrowot.coap.affordance import generate_subsite
from retrowot.coap.discovery_affordance import (
    DiscoverDeviceResource,
    DiscoverServiceResource,
)
from retrowot.configs import logger, settings
from retrowot.thing_description.publish import add_thing_description_to_thing_directory
from retrowot.thing_description_translation import (
    align_capabilities,  # , enrich_affordance
)
from retrowot.utils import Emitter


class CoAPServer:
    """
    Represents a CoAP server.

    Attributes:
        sites (Dict[str, Site]): A dictionary of sites.
        devices (Dict[str, Any]): A dictionary of devices.
        emitters (Emitter): An emitter for event handling.
        main_site (Site): The main site.
        server (Context): The server context.

    Methods:
        shutdown: Shuts down the server and disconnects from all devices.
        _initialize_emitters: Initializes the emitters for device discovery and affordance discovery.
        _initialize_sites: Initializes the sites for device and service discovery.
        run: Runs the CoAP server.

    """

    sites: Dict[str, Site] = {}
    devices: Dict[str, Any] = {}
    emitters = Emitter()
    main_site: Site = Site()
    server: Context = None

    async def shutdown(self) -> None:
        """
        Shuts down the server and disconnects from all devices.

        This method disconnects from all devices and shuts down the server if it is running.
        Args:
            self: The current instance of the class.

        Returns:
            None
        """
        print("Shutting down server")
        c = Client()
        for target_address in self.devices.keys():
            peer = await c.connect(target_address)
            await c.disconnect(target_address, peer)
        if self.server is not None:
            await self.server.shutdown()

        asyncio.get_event_loop().stop()

    def _initialize_emitters(self) -> None:
        """
        Initializes the emitters for device discovery and affordance discovery.

        This method sets up event listeners for device discovery and affordance discovery.
        It also enables enrichment and thing directory functionalities based on the settings.

        Args:
            self: The current instance of the class.

        Returns:
            None
        """

        logger.debug(
            "Initializing emitters for service alignment and sub-site generation"
        )
        self.emitters.device_discovery_emitter.on(
            "services_discovered",
            partial(
                align_capabilities, emitter=self.emitters.device_affordance_emitters
            ),
        )
        self.emitters.device_affordance_emitters.on(
            "thing_description_created",
            partial(generate_subsite, site=self.main_site, subsites=self.sites),
        )

        if settings.enrichment.use_enrichment:
            logger.debug("Enabling affordance enrichment...")
            self.emitters.device_discovery_emitter.on(
                "affordance_aligned", align_capabilities
            )

        if settings.thing_directory.use_thing_directory:
            logger.debug("Enabling thing directory...")
            self.emitters.device_affordance_emitters.on(
                "add_thing_description_to_thing_directory",
                add_thing_description_to_thing_directory,
            )

    def _initialize_sites(self) -> None:
        """
        Initializes the sites for device and service discovery.

        This method adds resources for device and service discovery to the main site.

        Args:
            None

        Returns:
            None
        """
        self.main_site.add_resource(
            ["device_discovery"], DiscoverDeviceResource(self.devices)
        )
        self.main_site.add_resource(
            ["service_discovery"],
            DiscoverServiceResource(
                self.devices, self.emitters.device_discovery_emitter
            ),
        )

        # Add the well-known core resource (Service Discovery)
        self.main_site.add_resource(
            [".well-known", "core"],
            WKCResource(self.main_site.get_resources_as_linkheader),
        )

    def __init__(self) -> None:

        self._initialize_emitters()
        self._initialize_sites()

    async def run(self) -> None:
        """
        Runs the CoAP server indefinitely.

        Example:
            >>> server = CoAPServer()
            >>> await server.run()
        """
        self.server = await Context.create_server_context(self.main_site)
        # Keep the server running
        await asyncio.Future()  # This keeps the server running indefinitely
