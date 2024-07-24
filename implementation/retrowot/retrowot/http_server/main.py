from functools import partial
from typing import Optional

import uvicorn
from configs import logger, settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from http_server.affordance import generate_subsite
from http_server.discovery import mainRouter
from thing_description.publish import add_thing_description_to_thing_directory
from thing_description_translation import align_capabilities  # , enrich_affordance
from utils import Emitter


class HTTPServer:
    _uvicorn_server: Optional[uvicorn.Server] = None
    server: Optional[FastAPI] = None
    emitters: Emitter = Emitter()

    def shutdown(self):
        logger.info("Shutting down HTTP server...")
        server = uvicorn.Server()
        server.shutdown(self.server)

    def __init__(self):
        logger.info("Initializing HTTP server...")
        logger.debug("Initializing HTTP server...")

        self.server = FastAPI()
        self.server.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.server.include_router(mainRouter)
        self.config = uvicorn.Config(
            self.server, host="0.0.0.0", port=8000, loop="asyncio"
        )
        self._uvicorn_server = uvicorn.Server(config=self.config)
        self._initialize_emitters()

    def _initialize_emitters(self):

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
            "thing_description_created", partial(generate_subsite, self.server)
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

    async def run(self):
        await self._uvicorn_server.serve()

    # def run(self):
    #    uvicorn.run(self.server, host="0.0.0.0", port=8000)
