import requests
import re
import geopy
import geopy.distance

def msGetAllStations():
    s = requests.Session()
    tmp = s.get("https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_fr.txt")
    descriptionLines = tmp.text.split('\n')
    cordinatesFound = False
    stationList = {}
    for line in descriptionLines:
        if not cordinatesFound :
            if(re.match(r"Stations\sCoordinates", line)):
                cordinatesFound = True
        else:
            if(re.match(r"^[A-Z]{3}\s+",line)):
                
                lineParts = None
                lineParts = re.split(r'\s\s+',line)
               
                
                ## Saving station data to a dictionnary
                stationData = {}
                stationData["code"] = lineParts[0]
                stationData["name"] = lineParts[1]
                stationData["lat"] = lineParts[2].split("/")[1]
                stationData["lon"] = lineParts[2].split("/")[0]
                stationData["coordianteKM"] = lineParts[3]
                stationData["altitude"] = lineParts[4].strip()
                
                stationList[lineParts[0]] = stationData
                
    return stationList 

def msGetClosestStation(currentLat,currnetLon):
    allStations = msGetAllStations()
    hPoint = geopy.Point(currentLat,currnetLon)
    data =[]
    for station in allStations:
        sPoint =geopy.Point(allStations[station]["lat"]+"/"+allStations[station]["lon"])
        distance = geopy.distance.distance(hPoint,sPoint)
        data += (distance.km,station),
        data.sort(key=lambda tup: tup[0])
    return data[0][1]
            