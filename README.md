[![](https://img.shields.io/github/release/websylv/homeassistant-meteoswiss/all.svg)](https://github.com/websylv/homeassistant-meteoswiss/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

  
  

# homeassistant-meteoswiss  

Home Assistant meteo swiss integration

## :warning: :warning: :warning: Upgrade form 0.6 or earlier :warning: :warning: :warning:
  

This intergration have been fully rewrited !

Is no longer compatible with the old configuration.

**Please remove old configuration before upgrade !**

In home configuration go to weather section and remove all the configuration related to platform meteo-swiss 

```YAML
weather:
  [...]
  - platform: meteo-swiss
    postcode: 1233
    [...]
```
restart you home assistant and then upgrade to the new version and proccced with the configuration part

## Information

Data from meteo swiss official website

The forecast is extracted from the meteo swiss website

Current conditions are from official data files.

## Installation


## Configuration

- Got to home assistant configuration :

![enter image description here](https://github.com/websylv/homeassistant-meteoswiss-img/raw/master/mRemoteNG_br58RnFLHN.png)
  
- Then click on "integrations":

![enter image description here](https://github.com/websylv/homeassistant-meteoswiss-img/raw/master/jDBoFYSD9L.png)

- Than add a new integration

![enter image description here](https://github.com/websylv/homeassistant-meteoswiss-img/raw/master/mRemoteNG_Xu9QUdjj7O.png)
  
- Search for "meteo-swiss"

![enter image description here](https://github.com/websylv/homeassistant-meteoswiss-img/raw/master/mRemoteNG_ZAipe8WopB.png)

- By default the integration will try to determine the best settings for you
based on you location:

![enter image description here](https://github.com/websylv/homeassistant-meteoswiss-img/raw/master/mRemoteNG_ZbyekuPQly.png)

If you are not happy with the settings you can update the settings

Meteo Swiss weather station code. This code can be found in : [https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_en.txt](https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_en.txt)\

  

## Debug

  

In case of problem with the integration

Please open an issue on github with the logs in debug mode.

You need to activate componenent debug log by adding "custom_components.meteo-swiss: debug" to your configuration.yaml

  

```YAML

logger:
default: warning
logs:
[...]
hamsclient.client: debug
custom_components.meteo-swiss: debug

```

  

## Privacy

  

This integration use :

  

https://nominatim.openstreetmap.org for geolocaliation if you don't set you post code

https://data.geo.admin.ch/ for current weather conditions

https://www.meteosuisse.admin.ch for forecast