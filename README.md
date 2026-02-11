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
Run it once and then you can play around with the project.

With most editors if you want to see documentation on micropython apis set
`poetry config virtualenvs.in-project true` before running `poetry install`.
Otherwise adjust `pyrightconfig.json` to include your venv location
