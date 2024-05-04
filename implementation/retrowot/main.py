from retrowot.coap.main import CoAPServer    
from retrowot.http_server.main import HTTPServer
import asyncio
from retrowot.configs import settings, logger
import signal

print(settings)

coap_server = None
http_server = None

async def shutdown_server(server):
    await server.shutdown()

async def shutdown_signal_handler(loop):
    if settings.server_type == "http":
        await shutdown_server(http_server)
    else:
        await shutdown_server(coap_server)

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    
    logger.debug("Server shutdown complete.")
    loop.stop()

def signal_handler(signum, frame):
    logger.debug('Signal received, shutting down...')
    asyncio.create_task(shutdown_signal_handler(loop))

if __name__ == "__main__":
    # Set its level to DEBUG
  
    
    loop = asyncio.get_event_loop()
    logger.info("Started server...")
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), signal_handler, signame, None)

    if settings.server_type == "http":
        http_server = HTTPServer()
        loop.run_until_complete(http_server.run())
    else:
        coap_server = CoAPServer()    
        loop.run_until_complete(coap_server.run())

    loop.close()
