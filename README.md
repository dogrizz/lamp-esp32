# what is this
Just some code to allow lamp to run LED Lamp using sunrise/sunset data

# setup
Need esp32.
Flash it with micropython.

Use below to set up secrets through nvs:
```
from esp32 import NVS

nvs = NVS("wifi")
nvs.set_blob("ssid", b"wifi_ssid")
nvs.set_blob("pass", b"wifi_pass")
nvs.commit()

nvs = NVS("weather")
nvs.set_blob("api_key", b"openweatherapikey")
nvs.commit()
```
Install microdot:
```
  mpremote connect auto mip install https://raw.githubusercontent.com/miguelgrinberg/microdot/refs/heads/main/src/microdot/microdot.py
```
Run it once and then you can play around with the project.

You will also need to install microdot. I was only able to install v1 (copy microdot.py and microdot_asyncio.py to lib dir on device) but if you have more RAM you should be able to run v2 without changing much of the code.

With most editors if you want to see documentation on micropython apis set
`poetry config virtualenvs.in-project true` before running `poetry install`.
Otherwise adjust `pyrightconfig.json` to include your venv location
