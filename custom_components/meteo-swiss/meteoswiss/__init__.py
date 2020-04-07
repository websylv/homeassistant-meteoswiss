"""meteoswiss - Library to get data from meteo swiss"""

__version__ = '0.0.11'
__author__ = 'websylv <div@webhu.org>'
__all__ = []

from .msStations import msGetAllStations
from .msStations import msGetClosestStation
from .msData import msGetCurrentCondition
from .msData import msGetForecast
from .misc import msGetWindBearing

