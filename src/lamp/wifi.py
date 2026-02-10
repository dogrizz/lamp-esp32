import network
import uasyncio as asyncio


class WiFiManager:
    def __init__(self, ssid: str, password: str):
        self.ssid: str = ssid
        self.password: str = password
        self.wlan = network.WLAN(network.STA_IF)
        self.connected: bool = False

    async def connect(self):
        if not self.wlan.active():
            self.wlan.active(True)

        if not self.wlan.isconnected():
            print("[wifi] connecting...")
            self.wlan.connect(self.ssid, self.password)

            # wait up to ~10 seconds
            for _ in range(20):
                if self.wlan.isconnected():
                    break
                await asyncio.sleep(0.5)

        self.connected = self.wlan.isconnected()
        if self.connected:
            print("[wifi] connected:", self.wlan.ifconfig())
        else:
            print("[wifi] connect failed")
            self.wlan.disconnect()

    async def keepalive(self):
        while True:
            if not self.wlan.isconnected():
                self.connected = False
                await self.connect()
            await asyncio.sleep(5)
