import uasyncio as asyncio
from machine import Pin

from wifi import WiFiManager


class StatusLED:
    def __init__(self, pin=2):
        self.led = Pin(pin, Pin.OUT)

    async def run(self, wifi: WiFiManager):
        while True:
            if wifi.connected:
                self.led.on()  # solid ON = connected
                await asyncio.sleep(1)
            else:
                # blink = not connected
                self.led.on()
                await asyncio.sleep(0.2)
                self.led.off()
                await asyncio.sleep(0.8)
