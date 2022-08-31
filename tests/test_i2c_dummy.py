from unittest import TestCase
from unittest.mock import patch
import bme280
import machine
import asyncio as uasyncio

# smbus.SMBus
class SMBusMock:
    def __init__(self, bus):
        assert bus == 42

    def close(self):
        pass

    def write_i2c_block_data(self, addr, reg, data):
        pass

    def read_i2c_block_data(self, addr, reg, length):
        if reg == 0xD0 and length == 1: # id
            return [ 0x60, ]
        if reg == 0x88 and length == 26: # cal burst 1
            return [ 0x01, ] * length
        if reg == 0xE1 and length == 7: # cal burst 2
            return [ 0x01, ] * length
        if reg == 0xF7 and length == 8: # value burst
            return [ 0x01, 0x02, 0x03,  # press
                     0x74, 0x75, 0x76,  # temp
                     0x18, 0x18, ]      # hum
        return [ 0, ] * length

# machine.I2C
class I2CMock(SMBusMock):
    def __init__(self, index=None, scl=None, sda=None, freq=None):
        if index is not None:
            assert index == 42
        assert freq is not None
        if isinstance(scl, PinMock):
            assert scl._pin == 11
        if isinstance(scl, int):
            assert scl == 11
        if isinstance(sda, PinMock):
            assert sda._pin == 12
        if isinstance(sda, int):
            assert sda == 12

    def deinit(self):
        pass

    def writeto_mem(self, addr, reg, data):
        self.write_i2c_block_data(addr, reg, data)

    def readfrom_mem(self, addr, reg, length):
        return bytes(self.read_i2c_block_data(addr, reg, length))

# machine.SoftI2C
class SoftI2CMock(I2CMock):
    def __init__(self, **kwargs):
        assert "index" not in kwargs
        I2CMock.__init__(self, **kwargs)

# machine.Pin
class PinMock:
    OPEN_DRAIN = object()

    def __init__(self, pin, mode, value):
        assert mode == self.OPEN_DRAIN
        assert value == 1
        self._pin = pin

class Test_I2CDummy(TestCase):
    @patch("bme280.bme280.isMicropython", False)
    @patch("smbus.SMBus", SMBusMock)
    def test_linux(self):
        with bme280.BME280(i2cBus=42) as bme:
            t, h, p = bme.readForced(filter=bme280.FILTER_4,
                                     tempOversampling=bme280.OVSMPL_4,
                                     humidityOversampling=bme280.OVSMPL_16,
                                     pressureOversampling=bme280.OVSMPL_4)
            #TODO

    @patch("bme280.bme280.isMicropython", True)
    @patch("machine.I2C", I2CMock, create=True)
    @patch("machine.SoftI2C", SoftI2CMock, create=True)
    @patch("machine.Pin", PinMock, create=True)
    def test_micropython(self):
        with bme280.BME280(i2cBus=42) as bme:
            t, h, p = bme.readForced()
        with bme280.BME280(i2cBus={ "index": 42, "scl": 11, "sda": 12 }) as bme:
            t, h, p = bme.readForced()
        with bme280.BME280(i2cBus={ "scl": 11, "sda": 12 }) as bme:
            t, h, p = bme.readForced()
        with bme280.BME280(i2cBus=machine.I2C(42, scl=11, sda=12, freq=100000)) as bme:
            t, h, p = bme.readForced()
        with bme280.BME280(i2cBus=machine.I2C(42,
                                              scl=machine.Pin(11, mode=machine.Pin.OPEN_DRAIN, value=1),
                                              sda=machine.Pin(12, mode=machine.Pin.OPEN_DRAIN, value=1),
                                              freq=100000)) as bme:
            t, h, p = bme.readForced()

        # Test async
        async def coroutine_():
            async with bme280.BME280(i2cBus=42) as bme:
                t, h, p = await bme.readForcedAsync()
        uasyncio.run(coroutine_())

# vim: ts=4 sw=4 expandtab
