import logging
import datetime
import pprint
import time
from typing import Any, cast
from async_timeout import timeout

from homeassistant.core import Config, HomeAssistant
from homeassistant.const import Platform, CONF_NAME
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.helpers import issue_registry as issues
from homeassistant.helpers.issue_registry import IssueSeverity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


from hamsclientfork import meteoSwissClient
from hamsclientfork.client import ClientResult
from .const import (
    DOMAIN,
    CONF_POSTCODE,
    CONF_STATION,
    CONF_ENABLESENSORS,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.WEATHER]
SCAN_INTERVAL = datetime.timedelta(minutes=1)
MAX_CONTINUOUS_ERROR_TIME = 60 * 60

async def async_setup(hass: HomeAssistant, config: Config):
    """Setup via configuration.yaml."""
    _LOGGER.debug("Async setup meteo swiss")

    conf = config.get(DOMAIN)
    if conf is None:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=conf
        )
    )
    _LOGGER.debug("END Async setup meteo swiss")
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})

    _LOGGER.debug("Current configuration: %s", config_entry.data)

    coordintaor = MeteoSwissDataUpdateCoordinator(
        hass,
        SCAN_INTERVAL,
        config_entry.data[CONF_POSTCODE],
        config_entry.data[CONF_STATION],
        config_entry.data[CONF_NAME]
    )

    await coordintaor.async_config_entry_first_refresh()

    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordintaor

    if config_entry.data[CONF_ENABLESENSORS]:
        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
        return True

    await hass.config_entries.async_forward_entry_setup(config_entry, Platform.WEATHER)
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(config_entry.entry_id)


class MeteoSwissClientResult(ClientResult):
    station: str
    post_code: str
    display_name: str


class MeteoSwissDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from meteoSwissClient."""

    data: MeteoSwissClientResult

    def __init__(
        self,
        hass: HomeAssistant,
        update_interval: datetime.timedelta,
        post_code: int,
        station: str | None,
        display_name: str,
    ) -> None:
        """Initialize."""
        self.first_error: float | None = None
        self.error_raised = False
        self.hass = hass
        self.post_code = post_code
        self.station = station
        self.display_name = display_name
        _LOGGER.debug(
            "Forecast %s will be provided for post code %s every %s",
            display_name,
            post_code,
            update_interval,
        )

        if station:
            _LOGGER.debug(
                "Real-time %s will be updated from %s every %s",
                display_name,
                station,
                update_interval,
            )

        self.client = meteoSwissClient(
            display_name,
            post_code,
            station if station else "NO STATION",
        )
        _LOGGER.debug("Client obtained")

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> MeteoSwissClientResult:
        """Update data via library."""
        try:
            async with timeout(15):
                data = await self.hass.async_add_executor_job(
                    self.client.get_typed_data,
                )
        except Exception as exc:
            raise UpdateFailed(exc) from exc

        _LOGGER.debug("Data obtained:\n%s", pprint.pformat(data))
        if self.station:
            if not data.get("condition"):
                # Oh no.  We could not retrieve the URL.
                # We try 20 times.  If it does not succeed,
                # we will induce a config error.
                _LOGGER.warning(
                    "Station %s provided us with no real-time data",
                    self.station,
                )
                if self.first_error is None:
                    self.first_error = time.time()

                m = MAX_CONTINUOUS_ERROR_TIME
                last_error = time.time() - self.first_error
                if not self.error_raised and last_error > m:
                    issues.async_create_issue(
                        self.hass,
                        DOMAIN,
                        f"{self.station}_provides_no_data_{DOMAIN}",
                        is_fixable=False,
                        is_persistent=False,
                        severity=IssueSeverity.ERROR,
                        translation_key="station_no_data",
                        translation_placeholders={
                            "station": self.station,
                        },
                    )
                    self.error_raised = True
            else:
                if self.error_raised:
                    issues.async_delete_issue(
                        self.hass, DOMAIN, f"{self.station}_provides_no_data_{DOMAIN}"
                    )
                self.first_error = None
                self.error_raised = False

        data[CONF_STATION] = self.station
        data[CONF_POSTCODE] = self.post_code
        data[CONF_NAME] = self.display_name
        return cast(MeteoSwissClientResult, data)
