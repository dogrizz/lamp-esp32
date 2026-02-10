import neopixel
import uasyncio as asyncio
from machine import Pin

LIT_UP = 1
FADE = 2


def gamma_scale(value, gamma=2.2) -> int:
    return int((int(value) / 255) ** gamma * 255)


class LedManager:
    def __init__(
        self, led_pin: int, number_of_leds: int, color: tuple, target_brightness: float
    ):
        self._np = neopixel.NeoPixel(pin=Pin(led_pin), n=number_of_leds)
        self.color = color
        if target_brightness > 1 or target_brightness < 0:
            raise ValueError("Invalid brightness")
        self.target_brightness = target_brightness

    def fill_strip(self, color, brightness):
        r, g, b = color
        scaled = (
            gamma_scale(r * brightness),
            gamma_scale(g * brightness),
            gamma_scale(b * brightness),
        )
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
            b = (i / steps) * self.target_brightness
            self.fill_strip(self.color, b)
            await asyncio.sleep(delay)

    async def bring_up(self, duration_s: int):
        print("[led_mgr] waking up")
        await self.blend_strip(duration_s, direction=LIT_UP)

    async def bring_down(self, duration_s: int):
        print("[led_mgr] bringing down")
        await self.blend_strip(duration_s, direction=FADE)

    async def run(self, duration_s: int):
        print("[led_mgr] running at target settings")
        self.fill_strip(self.color, self.target_brightness)
        await asyncio.sleep(duration_s)

    def clear(self):
        print("[led_mgr] Clearing leds")
        for i in range(len(self._np)):
            self._np[i] = (0, 0, 0)
        self._np.write()
