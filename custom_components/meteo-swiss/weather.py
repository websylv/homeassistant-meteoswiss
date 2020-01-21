import requests
from datetime import timedelta
import logging
import csv
import meteoswiss as ms

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    WeatherEntity,
)
import homeassistant.util.dt as dt_util
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import Throttle
import async_timeout
_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

CONDITION_CLASSES = {
    "clear-night": [101,102],
    "cloudy": [5,35,103,104,105],
    "fog": [27,28],
    "hail": [],
    "lightning": [12],
    "lightning-rainy": [13,23,24,25,32,106],
    "partlycloudy": [2,3,4],
    "pouring": [20],
    "rainy": [6,9,14,17,33],
    "snowy": [8,11,16,19,22,30,34],
    "snowy-rainy": [7,10,15,18,21,29,31,107],
    "sunny": [1,26],
    "windy": [],
    "windy-variant": [],
    "exceptional": [],
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    _LOGGER.info("Starting asnyc setup platform")
  

    async_add_entities([MeteoSwissWeather(config)], True)


class MeteoSwissWeather(WeatherEntity):
    def __init__(self, config):
        """Initialise the platform with a data instance and station name."""

        self._station_name = None
        self._condition = None
        self._forecast = None
        self._description = None
        _LOGGER.debug("meteo-swiss INIT")

        with async_timeout.timeout(10):
            allStation = ms.get_all_stations()
            self._station_name = allStation['GVE']['name']

    async def async_update(self):
        """Update Condition and Forecast."""
        _LOGGER.debug("meteo-swiss async update")
        
        with async_timeout.timeout(10):
            self._condition = ms.get_current_condition("GVE")
            self._forecastData = ms.get_forecast("1233")
            
        
        #with async_timeout.timeout(10):    
    @property
    def name(self):
        return self._station_name
    @property
    def temperature(self):
        return float(self._condition[0]['tre200s0'])
    @property
    def pressure(self):
        return float(self._condition[0]['prestas0'])
    @property
    def state(self):
        symbolId = self._forecastData["data"]['weather_symbol_id']
        return "sunny"
    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS
    @property
    def humidity(self):
        """Return the name of the sensor."""
        return float(self._condition[0]['ure200s0'])
    @property
    def wind_speed(self):
        """Return the name of the sensor."""
        return float(self._condition[0]['fu3010z0'])
    @property
    def attribution(self):
        return "MeteoSwiss"
    @property
    def wind_bearing(self):
        return ms.get_wind_bearing(self._condition[0]['dkl010z0'])
   
    
    