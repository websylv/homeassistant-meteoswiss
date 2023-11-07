import logging
import pprint

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity


from . import MeteoSwissDataUpdateCoordinator
from .const import (
    DOMAIN,
    SENSOR_TYPES,
    SENSOR_TYPE_CLASS,
    SENSOR_TYPE_ICON,
    SENSOR_TYPE_NAME,
    SENSOR_TYPE_UNIT,
    SENSOR_DATA_ID,
    CONF_STATION,
    CONF_POSTCODE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Setup all sensors"""
    _LOGGER.debug("Starting asnyc setup of sensor platform")
    coordinator: MeteoSwissDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    if coordinator.station:
        async_add_entities(
            [
                MeteoSwissSensor(config_entry.entry_id, sensor_type, coordinator)
                for sensor_type in SENSOR_TYPES
            ],
            True,
        )
    else:
        _LOGGER.info("The station %s has no real time data", config_entry.entry_id)


class MeteoSwissSensor(
    CoordinatorEntity[MeteoSwissDataUpdateCoordinator],
    SensorEntity,
):
    """The MeteoSwiss Sensor."""

    def __init__(
        self,
        integration_id: str,
        sensor_type,
        coordinator: MeteoSwissDataUpdateCoordinator,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = "sensor.%s-%s" % (integration_id, sensor_type)
        self._state = None
        self._type = sensor_type
        self._data = coordinator.data
        self._attr_station = coordinator.data[CONF_STATION]
        self._attr_post_code = coordinator.data[CONF_POSTCODE]

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._data[CONF_NAME]} {SENSOR_TYPES[self._type][SENSOR_TYPE_NAME]}"

    @property
    def state(self):
        """Return the state of the sensor."""
        dataId = SENSOR_TYPES[self._type][SENSOR_DATA_ID]
        if "condition" not in self._data or not self._data["condition"]:
            return STATE_UNAVAILABLE
        try:
            return self._data["condition"][0][dataId]
        except:
            _LOGGER.warn("Station returned bad data:\n%s", pprint.pformat(self._data))
            return STATE_UNAVAILABLE

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][SENSOR_TYPE_UNIT]

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES[self._type][SENSOR_TYPE_ICON]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][SENSOR_TYPE_CLASS]
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update of the sensor."""
        self._data = self.coordinator.data
        self.async_write_ha_state()
