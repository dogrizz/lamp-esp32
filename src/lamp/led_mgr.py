import neopixel
import uasyncio as asyncio
from machine import Pin

LIT_UP = 1
FADE = 2
FULL_ON = 1.0
FULL_OFF = 0


def gamma_scale(progress: float, target: int, gamma=2.2) -> int:
    corrected = progress**gamma
    return int(corrected * target)


class LedManager:
    def __init__(
        self, led_pin: int, number_of_leds: int, color: tuple, target_brightness: float
    ):
        self._np = neopixel.NeoPixel(pin=Pin(led_pin), n=number_of_leds)
        if target_brightness > 1 or target_brightness < 0:
            raise ValueError("Invalid brightness")
        r, g, b = color
        self.color = (
            int(r * target_brightness),
            int(g * target_brightness),
            int(b * target_brightness),
        )
        self.current = (0, 0, 0)
        self.status = "init"

    def fill_strip(self, color, progress):
        r, g, b = color
        scaled = (
            gamma_scale(progress, r),
            gamma_scale(progress, g),
            gamma_scale(progress, b),
        )
        self.current = scaled
        print(f"[led_mgr] Filling leds with {scaled}")
        for i in range(len(self._np)):
            self._np[i] = scaled
        self._np.write()

    async def blend_strip(self, duration: int, direction: int, steps=80):
        delay = duration / steps
        step_range = None
        if direction == LIT_UP:
            step_range = range(steps + 1)
        elif direction == FADE:
            step_range = range(steps, -1, -1)
        else:
            raise ValueError("Invalid direction")

        for i in step_range:
            b = i / steps
            self.fill_strip(self.color, b)
            await asyncio.sleep(delay)

    async def bring_up(self, duration_s: int):
        print("[led_mgr] waking up")
        self.status = "lighting up"
        await self.blend_strip(duration_s, direction=LIT_UP)

    async def bring_down(self, duration_s: int):
        self.status = "dimming"
        print("[led_mgr] bringing down")
        await self.blend_strip(duration_s, direction=FADE)

    async def run(self, duration_s: int):
        self.status = "running"
        print("[led_mgr] running at target settings")
        self.fill_strip(self.color, FULL_ON)
        await asyncio.sleep(duration_s)

    def clear(self):
        self.status = "off"
        print("[led_mgr] Clearing leds")
        self.fill_strip((0, 0, 0), FULL_OFF)
