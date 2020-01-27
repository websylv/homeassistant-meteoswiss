
# homeassistant-meteoswiss

Home Assistant meteo swiss integration

## Information

Data from meteo swiss official website
The forecast is from the site
Current conditions

## Configuration

Automatic configuration based on your location:

`
# Example configuration.yaml entry  
weather:
    - platform: meteo-swiss
`

Forced configuration:

`     
# Example configuration.yaml entry  
weather:
    - platform: meteo-swiss
      postcode: 1201 #Geneva post code
      station: GVE #Cointrin weather station
`

## Configuration variables
**postcode** 
	(string)(Optional)
	Post code of the location for the forecast. 
	If not provided the post code is determined by the location configured in home assistant
	
**station**
	(string)(Optional)
	Meteo Swiss weather station code. This code can be found in : [https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_en.txt](https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_en.txt)
	If not provided the closest from you location is use

**displayTime**
	(boolean)(Optional)
	Display time information next to the location. Enable by default
    	