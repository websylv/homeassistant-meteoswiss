import logging
from typing import cast

from hamsclientfork.client import DayForecast

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_TIME,
    WeatherEntity,
    WeatherEntityFeature,
    Forecast,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import TEMP_CELSIUS, SPEED_KILOMETERS_PER_HOUR, PRESSURE_HPA, CONF_NAME, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity


from . import MeteoSwissDataUpdateCoordinator, MeteoSwissClientResult
from .const import CONDITION_CLASSES, CONDITION_MAP, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup the weather entity."""
    _LOGGER.debug(
        "Add MeteoSwiss weather entity from config_entry %s" % config_entry.entry_id
    )

    coordinator: MeteoSwissDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    async_add_entities([MeteoSwissWeather(config_entry.entry_id, coordinator)], True)


class MeteoSwissWeather(
    CoordinatorEntity[MeteoSwissDataUpdateCoordinator], WeatherEntity
):
    _attr_has_entity_name = True
    _attr_native_temperature_unit = TEMP_CELSIUS
    _attr_native_pressure_unit = PRESSURE_HPA
    _attr_native_wind_speed_unit = SPEED_KILOMETERS_PER_HOUR
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY

    def __init__(
        self, integration_id: str, coordinator: MeteoSwissDataUpdateCoordinator
    ):
        super().__init__(coordinator)
        self._attr_unique_id = "weather.%s" % integration_id
        self.__set_data(coordinator.data)

    def __set_data(self, data: MeteoSwissClientResult) -> None:
        self._displayName = data[CONF_NAME]
        self._forecastData = data["forecast"]
        self._condition = data["condition"]

    @callback
    def _handle_coodinator_update(self):
        """Update Condition and Forecast."""
        data = self.coordinator.data
        self.__set_data(data)
        self.async_write_ha_state()

    @property
    def name(self):
        return self._displayName

    @property
    def native_temperature(self):
        if not self._condition:
            return
        try:
            return float(self._condition[0]["tre200s0"])
        except:
            _LOGGER.error("Error converting temp %s", self._condition)

    @property
    def native_pressure(self):
        if not self._condition:
            return
        try:
            return float(self._condition[0]["prestas0"])
        except:
            _LOGGER.error("Error converting pressure (qfe) %s", self._condition)

    @property
    def pressure_qff(self):
        if not self._condition:
            return
        try:
            return float(self.condition[0]["pp0qffs0"])
        except:
            _LOGGER.error("Error converting pressure (qff) %s", self._condition)

    @property
    def pressure_qnh(self):
        if not self._condition:
            return
        try:
            return float(self.condition[0]["pp0qnhs0"])
        except:
            _LOGGER.debug("Error converting pressure (qnh) %s", self._condition)

    @property
    def state(self):
        symbolId = self._forecastData["currentWeather"]["icon"]
        try:
            cond = next(
                (k for k, v in CONDITION_CLASSES.items() if int(symbolId) in v),
                None,
            )
            if cond is None:
                _LOGGER.error("Expected an integer for the forecast icon", symbolId)
                return STATE_UNAVAILABLE
            _LOGGER.debug("Current symbol is %s condition is : %s" % (symbolId, cond))
        except TypeError as exc:
            _LOGGER.error(
                "Expected an integer, not %r, to decide on the forecast icon: %s",
                symbolId,
                exc,
            )
            _LOGGER.error("Forecast data: %r", self._forecastData)
            return STATE_UNAVAILABLE
        return cond

    def msSymboldId(self):
        return self._forecastData["currentWeather"]["icon"]

    @property
    def humidity(self):
        if not self._condition:
            return
        try:
            return float(self._condition[0]["ure200s0"])
        except:
            _LOGGER.error("Unable to convert humidity value : %s", self._condition)

    @property
    def native_wind_speed(self):
        if not self._condition:
            return
        try:
            return float(self._condition[0]["fu3010z0"])
        except:
            _LOGGER.error("Unable to convert windSpeed value : %s", self._condition)

    @property
    def attribution(self):
        return "Weather forecast from MeteoSwiss (https://www.meteoswiss.admin.ch/)"

    @property
    def wind_bearing(self):
        if not self._condition:
            return
        try:
            return self._condition[0]["dkl010z0"]
        except:
            _LOGGER.error("Unable to get wind_bearing from data : %s", self._condition)

    def _forecast(self) -> list[Forecast] | None:
        fcdata_out = []
        for untpyed_forecast in self._forecastData["regionForecast"]:
            forecast = cast(DayForecast, untpyed_forecast)
            data_out = {}
            data_out[ATTR_FORECAST_TIME] = forecast["dayDate"]
            data_out[ATTR_FORECAST_NATIVE_TEMP_LOW] = float(forecast["temperatureMin"])
            data_out[ATTR_FORECAST_NATIVE_TEMP] = float(forecast["temperatureMax"])
            data_out[ATTR_FORECAST_CONDITION] = CONDITION_MAP.get(forecast["iconDay"])
            fcdata_out.append(data_out)
        return fcdata_out

    @property
    def forecast(self) -> list[Forecast]:
        """Return the forecast array."""
        return self._forecast()

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units."""
        return self._forecast()
