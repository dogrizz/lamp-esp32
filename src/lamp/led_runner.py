import time

import neopixel
import uasyncio as asyncio
from led_mgr import LedManager
from machine import Pin
from sun_data import SunDataFetcher

LED_DIM_TIME = 30 * 60  # seconds
UNIX_OFFSET = 946684800


def calc_delay_t(target_time: tuple) -> int:
    return calc_delay(hour=target_time[3], minute=target_time[4], second=target_time[5])


def calc_delay(hour, minute, second) -> int:
    now = time.localtime()  # (year, mon, day, hour, min, sec, wday, yday)
    delay = (hour - now[3]) * 3600 + (minute - now[4]) * 60 + (second - now[5])
    if delay < 0:
        delay += 24 * 3600  # schedule for next day
    print(f"[led] calculated delay = {delay}")
    return delay


async def wait_until(hour, minute=0, second=0):
    delay = calc_delay(hour, minute, second)
    await asyncio.sleep(delay)


async def wait_until_t(target_time: tuple):
    await wait_until(hour=target_time[3], minute=target_time[4], second=target_time[5])


class LedRunner:
    _turn_on: tuple
    _turn_off: tuple

    def __init__(
        self,
        sun_data_fetcher: SunDataFetcher,
        led_mgr: LedManager,
        max_lamp_time_s: int,
    ):
        self.sun_data_fetcher: SunDataFetcher = sun_data_fetcher
        self.led_mgr = led_mgr
        self.max_lamp_time = max_lamp_time_s

    def calculate(self, sun_data):
        self._turn_on = time.localtime(sun_data.sunrise - UNIX_OFFSET)
        self._turn_off = time.localtime(
            sun_data.sunrise + self.max_lamp_time - UNIX_OFFSET
        )
        print(f"[led] calculated lamp start: {self._turn_on} and end {self._turn_off}")

    async def run(self):
        self.led_mgr.clear()
        self.calculate(await self.sun_data_fetcher.fetch_sun_data())
        while True:
            on = time.mktime(self._turn_on)
            off_dim_start = time.mktime(self._turn_off) - LED_DIM_TIME
            if time.time() < on:
                print("[led] waiting till lamp start")
                await wait_until_t(self._turn_on)
            if time.time() <= (off_dim_start - LED_DIM_TIME):
                await self.led_mgr.bring_up(LED_DIM_TIME)
            if time.time() <= off_dim_start:
                await self.led_mgr.run(calc_delay_t(time.localtime(off_dim_start)))
                await self.led_mgr.bring_down(LED_DIM_TIME)
            self.led_mgr.clear()
            print("[led] waiting for next sync")
            await wait_until(hour=2)
            self.calculate(await self.sun_data_fetcher.fetch_sun_data())
