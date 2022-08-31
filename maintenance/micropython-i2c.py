import bme280
import time

with bme280.BME280(i2cBus=0) as bme:
    while True:
        t, h, p = bme.readForced(filter=bme280.FILTER_4,
                                 tempOversampling=bme280.OVSMPL_4,
                                 humidityOversampling=bme280.OVSMPL_16,
                                 pressureOversampling=bme280.OVSMPL_4)
        print("t=%.2f  h=%.2f  p=%.1f" % (t, h * 1e2, p * 1e-2))
        time.sleep_ms(1000)
