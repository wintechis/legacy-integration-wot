from configs import logger
from thing_description.thing_description import ThingDescription

async def add_thing_description_to_thing_directory(device) -> None:
    """
    Adds the thing description of a device to the thing directory.

    Args:
        device: The device object containing the thing description.

    Returns:
        None

    Example:
        >>> device = Device()
        >>> await add_thing_description_to_thing_directory(device)
    """
    logger.debug("Adding thing description to thing directory...")
    thing_description: ThingDescription = device.thing_description
    await thing_description.publish_thing_description()
        