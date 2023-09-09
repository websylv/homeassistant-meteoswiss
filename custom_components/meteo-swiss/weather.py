"""Support for the MeteoSwiss service."""
from __future__ import annotations
from hamsclient import meteoSwissClient

import datetime
import logging

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_TIME,
    WeatherEntity,
    WeatherEntityFeature,
    Forecast
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    TEMP_CELSIUS,
    SPEED_KILOMETERS_PER_HOUR,
    PRESSURE_HPA
)

from .const import (
    CONDITION_CLASSES,
    CONDITION_MAP,
    DOMAIN
)
from homeassistant.core import HomeAssistant, callback

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    _LOGGER.info("Add a MeteoSwiss weather entity from a config_entry.")
    client = hass.data[DOMAIN]['client']
    async_add_entities([MeteoSwissWeather(client)], True)

class MeteoSwissWeather(WeatherEntity):
    _attr_has_entity_name = True
    _attr_native_temperature_unit = TEMP_CELSIUS
    _attr_native_pressure_unit = PRESSURE_HPA
    _attr_native_wind_speed_unit = SPEED_KILOMETERS_PER_HOUR
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
    
    def __init__(self, client: meteoSwissClient):
        self._client = client
        if client is None:
            _LOGGER.error("Error empty client")

    def update(self):
        """Update Condition and Forecast."""
        self._client.update()
        data = self._client.get_data()
        self._displayName = data["name"]
        self._forecastData = data["forecast"]
        self._condition = data["condition"]

    @property
    def name(self):
       return  self._displayName

    @property
    def native_temperature(self):
        try:
            return float(self._condition[0]['tre200s0'])
        except:
            _LOGGER.debug("Error converting temp %s"%self._condition[0]['tre200s0'])
            return None
    @property
    def native_pressure(self):
        try:
            return float(self._condition[0]['prestas0'])
        except:
            _LOGGER.debug("Error converting pressure (qfe) %s"%self._condition[0]['prestas0'])
            return None
    @property
    def pressure_qff(self):
        try:
            return float(self.condition[0]['pp0qffs0'])
        except:
            _LOGGER.debug("Error converting pressure (qff) %s"%self._condition[0]['pp0qffs0'])
            return None

    @property
    def pressure_qnh(self):
        try:
            return float(self.condition[0]['pp0qnhs0'])
        except:
            _LOGGER.debug("Error converting pressure (qnh) %s"%self._condition[0]['pp0qnhs0'])
            return None
    @property
    def state(self):
        symbolId = self._forecastData["currentWeather"]['icon']
        cond =  next(
                    (
                        k
                        for k, v in CONDITION_CLASSES.items()
                        if int(symbolId) in v
                    ),
                    None,
                )
        _LOGGER.debug("Current symbol is %s condition is : %s"%(symbolId,cond))
        return cond

    def msSymboldId(self):
        return self._forecastData["currentWeather"]['icon']
    

    @property
    def humidity(self):
        try:
            return float(self._condition[0]['ure200s0'])
        except:
            _LOGGER.debug("Unable to convert humidity value : %s"%(self._condition[0]['ure200s0']))
    
    @property
    def native_wind_speed(self):
        try:
            return float(self._condition[0]['fu3010z0'])
        except:
            _LOGGER.debug("Unable to convert windSpeed value : %s"%(self._condition[0]['fu3010z0']))
            return None

    @property
    def attribution(self):
        return "Weather forecast from MeteoSwiss (https://www.meteoswiss.admin.ch/)"
    
    @property
    def wind_bearing(self):
        try:
            client = self._client.get_client()
            return client.get_wind_bearing(self._condition[0]['dkl010z0'])
        except:
            _LOGGER.debug("Unable to get wind_bearing from data : %s"%(self._condition[0]['dkl010z0']))
            return None
    
    def _forecast(self) -> list[Forecast] | None: 
        currentDate = datetime.datetime.now()
        one_day = datetime.timedelta(days=1)
        fcdata_out = []
        # Skip the first element - it's the forecast for the current day
        for forecast in self._forecastData["regionForecast"][1:]:
            #calculating date of the forecast
            currentDate = currentDate + one_day
            data_out = {}
            data_out[ATTR_FORECAST_TIME] = currentDate.strftime("%Y-%m-%d")
            data_out[ATTR_FORECAST_NATIVE_TEMP_LOW]=float(forecast["temperatureMin"])
            data_out[ATTR_FORECAST_NATIVE_TEMP]=float(forecast["temperatureMax"])
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
