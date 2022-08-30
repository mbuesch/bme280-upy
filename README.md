# BME-280 sensor device driver with Micropython and Linux support (I2C + SPI)

[Project website](https://bues.ch/)

[Git repository](https://bues.ch/cgit/bme280-upy.git)

This driver runs on Micropython and on regular Python (e.g. Raspberry Pi or other Linux devices).

It has support for both I2C and SPI bus.

# Example: I2C

    import bme280

    try:
        # Connect to BME-280 via I2C-0 hardware with default pinning:
        bme = bme280.BME280(i2cBus=0)

        # Alternatively:
        # Connect to BME-280 via I2C-0 hardware with custom pinning (not supported by all microcontrollers):
        #bme = bme280.BME280(i2cBus={ "index": 0, "scl": 1, "sda": 0 })

        # Alternatively:
        # Connect to BME-280 via software I2C with custom pinning (not supported by all microcontrollers):
        #bme = bme280.BME280(i2cBus={ "scl": 1, "sda": 0 })

        # Alternatively:
        # Connect to BME-280 via pre-initialized Micropython bus object:
        #bme = bme280.BME280(i2cBus=machine.I2C(0, ...))

        # Synchronously trigger a MODE_FORCED conversion and return the result.
        temperature, humidity, pressure = bme.readForced(filter=bme280.FILTER_2,
                                                         tempOversampling=bme280.OVSMPL_4,
                                                         humidityOversampling=bme280.OVSMPL_4,
                                                         pressureOversampling=bme280.OVSMPL_4)

        # See help(bme280.BME280) for documentation and more methods.

        # Print the result.
        print(f"{temperature:.1f} *C; {humidity * 100:.1f} % rel. hum.; {pressure / 100:.1f} hPa")

    except bme280.BME280Error as e:
        print(f"BME280 error: {e}")

# Example: SPI

    import bme280

    try:
        # Connect to BME-280 via SPI-0 hardware with default pinning and pin 5 as chip select:
        bme = bme280.BME280(spiBus=0, spiCS=5)

        # Alternatively:
        # Connect to BME-280 via SPI-0 hardware with custom pinning (not supported by all microcontrollers):
        #bme = bme280.BME280(spiBus={ "index": 0, "sck": 1, "mosi": 2, "miso": 3 }, spiCS=5)

        # Alternatively:
        # Connect to BME-280 via software SPI with custom pinning (not supported by all microcontrollers):
        #bme = bme280.BME280(spiBus={ "sck": 1, "mosi": 2, "miso": 3 }, spiCS=5)

        # Alternatively:
        # Connect to BME-280 via pre-initialized Micropython bus object:
        #bme = bme280.BME280(spiBus=machine.SPI(0, ...), spiCS=machine.Pin(5, ...))

        # Synchronously trigger a MODE_FORCED conversion and return the result.
        temperature, humidity, pressure = bme.readForced(filter=bme280.FILTER_2,
                                                         tempOversampling=bme280.OVSMPL_4,
                                                         humidityOversampling=bme280.OVSMPL_4,
                                                         pressureOversampling=bme280.OVSMPL_4)

        # See help(bme280.BME280) for documentation and more methods.

        # Print the result.
        print(f"{temperature:.1f} *C; {humidity * 100:.1f} % rel. hum.; {pressure / 100:.1f} hPa")

    except bme280.BME280Error as e:
        print(f"BME280 error: {e}")

# Example: Context Manager

The BME280 instance can also be used as Context Manager (Python `with` statement).

    import bme280

    try:
        with bme280.BME280(i2cBus=0) as bme:
            temperature, humidity, pressure = bme.readForced(filter=bme280.FILTER_2,
                                                             tempOversampling=bme280.OVSMPL_4,
                                                             humidityOversampling=bme280.OVSMPL_4,
                                                             pressureOversampling=bme280.OVSMPL_4)
            # ...
    except bme280.BME280Error as e:
        print(f"BME280 error: {e}")

# License

Copyright (c) 2020-2022 Michael Büsch <m@bues.ch>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
