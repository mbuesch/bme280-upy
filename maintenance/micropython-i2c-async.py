import bme280
import uasyncio

async def example():
    async with bme280.BME280(i2cBus=0) as bme:
        while True:
            t, h, p = await bme.readForcedAsync(filter=bme280.FILTER_4,
                                                tempOversampling=bme280.OVSMPL_4,
                                                humidityOversampling=bme280.OVSMPL_16,
                                                pressureOversampling=bme280.OVSMPL_4)
            print("t=%.2f  h=%.2f  p=%.1f" % (t, h * 1e2, p * 1e-2))
            uasyncio.sleep(1)

uasyncio.run(example())

# vim: ts=4 sw=4 expandtab
