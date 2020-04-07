import pandas as pd
from bs4 import BeautifulSoup
import json
import requests
import logging
_LOGGER = logging.getLogger(__name__)

def msGetCurrentCondition(station):
    data = pd.read_csv("https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv",sep=';',header=1)
    stationData = data.loc[data['stn'].str.contains(station)]
    stationData = stationData.to_dict('records')
    return stationData


def msGetForecast(postCode):
    baseUrl = 'https://www.meteosuisse.admin.ch'

    s = requests.Session()
    #Forcing headers to avoid 500 error when downloading file
    s.headers.update({"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding":"gzip, deflate, sdch",'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/1337 Safari/537.36'})
    mainUrl = "https://www.meteosuisse.admin.ch/home/actualite/infos.html?ort=%s"%postCode
    _LOGGER.debug("Main URL : %s"%mainUrl)
    tmp = s.get(baseUrl)

    soup = BeautifulSoup(tmp.text,features="html.parser")
    widgetHtml = soup.find_all("section",{"id": "weather-widget"})
    jsonUrl = widgetHtml[0].get("data-json-url")
    jsonDataFile = str.split(jsonUrl,'/')[-1]
    newJsonDataFile = str(postCode)+"00.json"
    jsonUrl = str(jsonUrl).replace(jsonDataFile,newJsonDataFile)
    dataUrl = baseUrl + jsonUrl
    _LOGGER.debug("Data URL : %s"%dataUrl)
    jsonData = s.get(dataUrl)
    jsonData.encoding = "utf8"
    jsonDataTxt = jsonData.text

    jsonObj = json.loads(jsonDataTxt)

    return jsonObj