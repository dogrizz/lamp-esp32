import time

import ntptime
import uasyncio as asyncio

from wifi import WiFiManager

SECONDS_IN_DAY = 86400


class TimeSync:
    def __init__(self, wifi: WiFiManager):
        self.wifi = wifi
        self.synced = False

    async def sync_time(self):
        while not self.wifi.connected:
            await asyncio.sleep(1)  # wait until Wi-Fi is up

        try:
            print("[time] syncing NTP...")
            ntptime.settime()  # sets RTC to UTC
            self.synced = True
            print("[time] synced:", time.localtime())
        except Exception as e:
            print("[time] sync failed:", e)
            self.synced = False

    async def daily_sync(self):
        """Re-sync every 24 hours"""
        while True:
            await self.sync_time()
            await asyncio.sleep(SECONDS_IN_DAY)
