from hamsclient import meteoSwissClient

import datetime
import logging

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_TIME,
    WeatherEntity
)
from homeassistant.const import (
    TEMP_CELSIUS,
    SPEED_KILOMETERS_PER_HOUR,
    PRESSURE_HPA
)

_LOGGER = logging.getLogger(__name__)


from .const import CONDITION_CLASSES,DOMAIN


async def async_setup_entry(hass, config, async_add_entities):
    _LOGGER.info("Starting asnyc setup platform")
    client =hass.data[DOMAIN]['client']
    async_add_entities([MeteoSwissWeather(client)], True)

class MeteoSwissWeather(WeatherEntity):
    _attr_native_temperature_unit = TEMP_CELSIUS
    _attr_native_pressure_unit = PRESSURE_HPA
    _attr_native_wind_speed_unit = SPEED_KILOMETERS_PER_HOUR
    
    def __init__(self,client:meteoSwissClient):
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
    
    @property
    def forecast(self): 
        currentDate = datetime.datetime.now()
        one_day = datetime.timedelta(days=1)
        fcdata_out = []
        # Skip the first element - it's the forecast for the current day
        for forecast in self._forecastData["regionForecast"]:
            #calculating date of the forecast
            data_out = {}
            data_out[ATTR_FORECAST_TIME] = currentDate.strftime("%Y-%m-%d")
            data_out[ATTR_FORECAST_NATIVE_TEMP_LOW]=float(forecast["temperatureMin"])
            data_out[ATTR_FORECAST_NATIVE_TEMP]=float(forecast["temperatureMax"])
            data_out[ATTR_FORECAST_CONDITION] = next(
                            (
                                k
                                for k, v in CONDITION_CLASSES.items()
                                if int(forecast["iconDay"]) in v
                            ),
                            None,
                        )
            currentDate = currentDate + one_day
            fcdata_out.append(data_out)
        return fcdata_out
        
        
    
