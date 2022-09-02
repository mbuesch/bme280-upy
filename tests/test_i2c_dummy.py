from unittest import TestCase
from unittest.mock import patch
import binascii
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
            return list(binascii.unhexlify("04719f673200198a4dd6d00bc419fafff9ff0c3020d18813004b"))
        if reg == 0xE1 and length == 7: # cal burst 2
            return list(binascii.unhexlify("5a01001626031e"))
        if reg == 0xF7 and length == 8: # value burst
            return list(binascii.unhexlify("5e962085efc07bd2"))
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
            self.assertTrue(t > 0 and h > 0 and p > 0)

        with bme280.BME280(i2cBus=42, calc=bme280.CALC_INT32) as bme:
            t, h, p = bme.readForced()
            self.assertAlmostEqual(t, 27.099998, places=4)
            self.assertAlmostEqual(h, 0.451729, places=4)
            self.assertAlmostEqual(p, 98484.001160, places=1)

        with bme280.BME280(i2cBus=42, calc=bme280.CALC_INT64) as bme:
            t, h, p = bme.readForced()
            self.assertAlmostEqual(t, 27.099998, places=4)
            self.assertAlmostEqual(h, 0.451729, places=4)
            self.assertAlmostEqual(p / 100, 984.84001160, places=1)

        with bme280.BME280(i2cBus=42, calc=bme280.CALC_FLOAT) as bme:
            t, h, p = bme.readForced()
            self.assertAlmostEqual(t, 27.099998, places=1)
            self.assertAlmostEqual(h, 0.451729, places=2)
            self.assertAlmostEqual(p / 100, 984.84001160, places=1)

    @patch("bme280.bme280.isMicropython", True)
    @patch("machine.I2C", I2CMock, create=True)
    @patch("machine.SoftI2C", SoftI2CMock, create=True)
    @patch("machine.Pin", PinMock, create=True)
    def test_micropython(self):
        with bme280.BME280(i2cBus=42) as bme:
            t, h, p = bme.readForced()
            self.assertTrue(t > 0 and h > 0 and p > 0)
        with bme280.BME280(i2cBus={ "index": 42, "scl": 11, "sda": 12 }) as bme:
            t, h, p = bme.readForced()
            self.assertTrue(t > 0 and h > 0 and p > 0)
        with bme280.BME280(i2cBus={ "scl": 11, "sda": 12 }) as bme:
            t, h, p = bme.readForced()
            self.assertTrue(t > 0 and h > 0 and p > 0)
        with bme280.BME280(i2cBus=machine.I2C(42, scl=11, sda=12, freq=100000)) as bme:
            t, h, p = bme.readForced()
            self.assertTrue(t > 0 and h > 0 and p > 0)
        with bme280.BME280(i2cBus=machine.I2C(42,
                                              scl=machine.Pin(11, mode=machine.Pin.OPEN_DRAIN, value=1),
                                              sda=machine.Pin(12, mode=machine.Pin.OPEN_DRAIN, value=1),
                                              freq=100000)) as bme:
            t, h, p = bme.readForced()
            self.assertTrue(t > 0 and h > 0 and p > 0)

        # Test async
        async def coroutine_():
            async with bme280.BME280(i2cBus=42) as bme:
                t, h, p = await bme.readForcedAsync()
                self.assertTrue(t > 0 and h > 0 and p > 0)
        uasyncio.run(coroutine_())

        # Normal mode
        with bme280.BME280(i2cBus=42) as bme:
            bme.start(mode=bme280.MODE_NORMAL,
                      standbyTime=bme280.T_SB_10ms)

        # Other methods
        with bme280.BME280(i2cBus=42) as bme:
            bme.readForced()
            self.assertFalse(bme.isMeasuring())
            bme.reset()

# vim: ts=4 sw=4 expandtab
