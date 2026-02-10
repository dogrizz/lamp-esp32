import led_mgr
import uasyncio as asyncio
from esp32 import NVS
from led_runner import LedRunner
from status_led import StatusLED
from sun_data import Coordinates, SunDataFetcher
from time_sync import TimeSync
from wifi import WiFiManager

COORDINATES = Coordinates(latitude=54.430378, longitude=18.4383987)
NUM_LEDS = 18
LED_PIN = 16
COLOR = (255, 160, 90)
BRIGHTNESS = 0.3
MAX_LAMP_TIME = 12 * 60 * 60  # seconds


def get_str(nvs: NVS, key: str) -> str:
    buf = bytearray(128)
    nvs.get_blob(key, buf)
    return buf.rstrip(b"\x00").decode()


nvs_wifi = NVS("wifi")
wifi = WiFiManager(get_str(nvs_wifi, "ssid"), get_str(nvs_wifi, "pass"))
status_led = StatusLED()
time_sync = TimeSync(wifi)
nvs_weather = NVS("weather")
sun_data_fetcher = SunDataFetcher(wifi, get_str(nvs_weather, "api_key"), COORDINATES)
led_mgr = led_mgr.LedManager(
    led_pin=LED_PIN, number_of_leds=NUM_LEDS, color=COLOR, target_brightness=BRIGHTNESS
)
led = LedRunner(sun_data_fetcher, led_mgr, MAX_LAMP_TIME)


async def main():
    asyncio.create_task(wifi.keepalive())
    asyncio.create_task(status_led.run(wifi))
    asyncio.create_task(time_sync.daily_sync())
    asyncio.create_task(led.run())
    await asyncio.Event().wait()


asyncio.run(main())
