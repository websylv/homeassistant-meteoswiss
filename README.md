
[![](https://img.shields.io/github/release/websylv/homeassistant-meteoswiss/all.svg)](https://github.com/websylv/homeassistant-meteoswiss/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)


# homeassistant-meteoswiss

Home Assistant meteo swiss integration

## Information

Data from meteo swiss official website
The forecast is from the site
Current conditions

## Configuration

Automatic configuration based on your location:

```YAML
# Example configuration.yaml entry  
weather:
    - platform: meteo-swiss
```

Forced configuration:

```YAML     
# Example configuration.yaml entry  
weather:
    - platform: meteo-swiss
      name: "MeteoSwiss" #Will use meteoSwiss as entity name 
      postcode: 1201 #Geneva post code
      station: GVE #Cointrin weather station
```

## Configuration variables

**name**  
*(string)(optional)*

By default the name of the entity is the weather station name provided by meteo swiss.  
Setting the name will override the automatic weather station name. 

**postcode**  
*(string)(Optional)*

Post code of the location for the forecast.   
If not provided the post code is determined by the location configured in home assistant
	
**station**  
*(string)(Optional)*

Meteo Swiss weather station code. This code can be found in : [https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_en.txt](https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_en.txt)\
If not provided the closest from you location is use

In case of problem with the integration
Please open an issue on github with the logs in debug mode.
You need to activate componenent debug log by adding "custom_components.meteo-swiss: debug" to your configuration.yaml 

## Debug

```YAML   
logger:
  default: warning
  logs:
    [...]
    custom_components.meteo-swiss: debug
```

## Privacy

This integration use :

https://nominatim.openstreetmap.org for geolocaliation if you don't set you post code  
https://data.geo.admin.ch/ for current weather conditions  
https://www.meteosuisse.admin.ch for forecast  