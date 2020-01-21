import requests
import logging
from homeassistant.core import Config, HomeAssistant
DOMAIN = 'meteo-swiss'
_LOGGER = logging.getLogger(__name__)



async def async_setup(hass: HomeAssistant, config: Config):
    _LOGGER.debug("Async setup meteo swiss")
    return True
