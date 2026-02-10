import uasyncio as asyncio
import ujson
import urequests
from wifi import WiFiManager


class Coordinates:
    def __init__(self, longitude: float, latitude: float):
        self.longitude = "{:.2f}".format(longitude)
        self.latitude = "{:.2f}".format(latitude)

    def __str__(self) -> str:
        return f"lon: {self.longitude} lat: {self.latitude}"


class SunData:
    def __init__(self, sunrise: int, sunset: int):
        self.sunrise = sunrise
        self.sunset = sunset


class SunDataFetcher:
    def __init__(self, wifi: WiFiManager, api_key: str, coords: Coordinates):
        self.wifi: WiFiManager = wifi
        self.api_key: str = api_key
        self.coords: Coordinates = coords

    async def fetch_sun_data(self) -> SunData:
        while not self.wifi.connected:
            await asyncio.sleep(1)
        try:
            print(f"[data] fetching sun data for {self.coords}")
            url = f"http://api.openweathermap.org/data/2.5/weather?appid={self.api_key}&units=metric&lat={self.coords.latitude}&lon={self.coords.longitude}"
            r = urequests.get(url)
            data = ujson.loads(r.text)
            sunrise = data["sys"]["sunrise"]
            sunset = data["sys"]["sunset"]
            r.close()
            print(f"[data] sunrise: {sunrise} sunset: {sunset}")
            return SunData(sunrise, sunset)
        except Exception as e:
            print("[data] error:", e)
            await asyncio.sleep(1)
            return await self.fetch_sun_data()
