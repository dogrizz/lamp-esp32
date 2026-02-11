import time

import uasyncio as asyncio
from esp32 import NVS
from led_mgr import LedManager
from led_runner import LedRunner
from microdot_asyncio import Microdot
from status_led import StatusLED
from sun_data import Coordinates, SunDataFetcher
from time_sync import TimeSync
from wifi import WiFiManager

COORDINATES = Coordinates(latitude=54.430378, longitude=18.4383987)
NUM_LEDS = 18
LED_PIN = 25
COLOR = (255, 160, 90)
BRIGHTNESS = 0.6
MAX_LAMP_TIME = 12 * 60 * 60  # seconds
STATUS_PORT = 80


def get_str(nvs: NVS, key: str) -> str:
    buf = bytearray(128)
    nvs.get_blob(key, buf)
    return buf.rstrip(b"\x00").decode()


def date_str(datetime) -> str:
    y, m, d, h, mi, s, _, _ = datetime
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(y, m, d, h, mi, s)


def color_str(color) -> str:
    r, g, b = color
    return f"(r:{r} g:{g} b:{b})"


app = Microdot()
nvs_wifi = NVS("wifi")
wifi = WiFiManager(get_str(nvs_wifi, "ssid"), get_str(nvs_wifi, "pass"))
status_led = StatusLED()
time_sync = TimeSync(wifi)
nvs_weather = NVS("weather")
sun_data_fetcher = SunDataFetcher(wifi, get_str(nvs_weather, "api_key"), COORDINATES)
led_manager = LedManager(
    led_pin=LED_PIN, number_of_leds=NUM_LEDS, color=COLOR, target_brightness=BRIGHTNESS
)
led = LedRunner(sun_data_fetcher, led_manager, MAX_LAMP_TIME)


@app.get("/info")
async def status(request):
    return {
        "name": "Lamp",
        "status": led_manager.status,
        "time": {
            "localtime": date_str(time.localtime()),
            "last_sync": date_str(time_sync.last_sync),
        },
        "color": {
            "current": color_str(led_manager.current),
            "target": color_str(led_manager.color),
        },
        "plan": {"on": date_str(led._turn_on), "off": date_str(led._turn_off)},
    }


async def main():
    asyncio.create_task(wifi.keepalive())
    asyncio.create_task(status_led.run(wifi))
    asyncio.create_task(time_sync.daily_sync())
    asyncio.create_task(led.run())
    asyncio.create_task(app.start_server(port=STATUS_PORT))
    await asyncio.Event().wait()


asyncio.run(main())
