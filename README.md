# BME-280 sensor device driver with Micropython support (I2C + SPI)

[Project website](https://bues.ch/)

[Git repository](https://bues.ch/cgit/bme280.git)

This driver runs on regular Python and on Micropython.

It has support for both I2C and SPI bus.

# Example

    import bme280

    try:
        # Connect to BME-280 via I2C.
        bme = bme280.BME280(i2cBus=0)

        # Synchronously trigger a MODE_FORCED conversion and return the result.
        temperature, humidity, pressure = bme.readForced(filter=bme280.FILTER_2,
                                                         tempOversampling=bme280.OVSMPL_4,
                                                         humidityOversampling=bme280.OVSMPL_4,
                                                         pressureOversampling=bme280.OVSMPL_4)

        # Print the result.
        print(f"{temperature:.1f} *C; {humidity * 100:.1f} % rel. hum.; {pressure / 100:.1f} hPa")

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
