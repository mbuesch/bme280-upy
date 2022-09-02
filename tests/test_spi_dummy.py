from unittest import TestCase
from unittest.mock import patch
import binascii
import bme280
import machine
import asyncio as uasyncio

# spidev.SpiDev
class SpiDevMock:
    def open(self, bus, cs):
        assert bus == 42 and cs == 2

    def close(self):
        pass

    def xfer2(self, data):
        length = len(data)
        assert length >= 1
        reg = data[0]
        if reg == 0xD0 and length == 1 + 1: # id
            return b'\0' + bytes([ 0x60, ])
        if reg == 0x88 and length == 26 + 1: # cal burst 1
            return b'\0' + binascii.unhexlify("04719f673200198a4dd6d00bc419fafff9ff0c3020d18813004b")
        if reg == 0xE1 and length == 7 + 1: # cal burst 2
            return b'\0' + binascii.unhexlify("5a01001626031e")
        if reg == 0xF7 and length == 8 + 1: # value burst
            return b'\0' + binascii.unhexlify("5e962085efc07bd2")
        return bytes([ 0, ] * length)

# machine.SPI
class SPIMock(SpiDevMock):
    MSB = object()

    def __init__(self, index=None, baudrate=None, *,
                 polarity=None, phase=None, bits=None, firstbit=None,
                 sck=None, mosi=None, miso=None):
        if index is not None:
            assert index == 42
        if polarity is not None:
            assert polarity == 0
        if phase is not None:
            assert phase == 0
        if bits is not None:
            assert bits == 8
        if firstbit is not None:
            assert firstbit == self.MSB
        if isinstance(sck, PinMock):
            assert sck._pin == 21
            assert sck._mode == PinMock.OUT
            assert sck._value == 0
        if isinstance(sck, int):
            assert sck == 21
        if isinstance(mosi, PinMock):
            assert mosi._pin == 22
            assert mosi._mode == PinMock.OUT
            assert mosi._value == 0
        if isinstance(mosi, int):
            assert mosi == 22
        if isinstance(miso, PinMock):
            assert miso._pin == 23
            assert miso._mode == PinMock.IN
            assert miso._value is None
        if isinstance(miso, int):
            assert miso == 23

    def deinit(self):
        pass

    def write(self, data):
        self.xfer2(data)

    def read(self, nbytes, write=0):
        return self.xfer2(bytes([write, ] * nbytes))

# machine.SoftSPI
class SoftSPIMock(SPIMock):
    def __init__(self, **kwargs):
        assert "index" not in kwargs
        SPIMock.__init__(self, **kwargs)

# machine.Pin
class PinMock:
    OUT = object()
    IN = object()

    def __init__(self, pin, mode, value=None):
        self._value = value
        self._mode = mode
        self._pin = pin

    def __call__(self, value=None):
        assert value is not None
        self._value = value

class Test_SPIDummy(TestCase):
    @patch("bme280.bme280.isMicropython", False)
    @patch("spidev.SpiDev", SpiDevMock)
    def test_linux(self):
        with bme280.BME280(spiBus=42, spiCS=2) as bme:
            t, h, p = bme.readForced(filter=bme280.FILTER_4,
                                     tempOversampling=bme280.OVSMPL_4,
                                     humidityOversampling=bme280.OVSMPL_16,
                                     pressureOversampling=bme280.OVSMPL_4)
            self.assertTrue(t > 0 and h > 0 and p > 0)

        with bme280.BME280(spiBus=42, spiCS=2, calc=bme280.CALC_INT32) as bme:
            t, h, p = bme.readForced()
            self.assertAlmostEqual(t, 27.099998, places=4)
            self.assertAlmostEqual(h, 0.451729, places=4)
            self.assertAlmostEqual(p, 98484.001160, places=1)

        with bme280.BME280(spiBus=42, spiCS=2, calc=bme280.CALC_INT64) as bme:
            t, h, p = bme.readForced()
            self.assertAlmostEqual(t, 27.099998, places=4)
            self.assertAlmostEqual(h, 0.451729, places=4)
            self.assertAlmostEqual(p / 100, 984.84001160, places=1)

        with bme280.BME280(spiBus=42, spiCS=2, calc=bme280.CALC_FLOAT) as bme:
            t, h, p = bme.readForced()
            self.assertAlmostEqual(t, 27.099998, places=1)
            self.assertAlmostEqual(h, 0.451729, places=2)
            self.assertAlmostEqual(p / 100, 984.84001160, places=1)

    @patch("bme280.bme280.isMicropython", True)
    @patch("machine.SPI", SPIMock, create=True)
    @patch("machine.SoftSPI", SoftSPIMock, create=True)
    @patch("machine.Pin", PinMock, create=True)
    def test_micropython(self):
        with bme280.BME280(spiBus=42, spiCS=2) as bme:
            t, h, p = bme.readForced()
            self.assertTrue(t > 0 and h > 0 and p > 0)
        with bme280.BME280(spiBus={ "index": 42, "sck": 21, "mosi": 22, "miso": 23 }, spiCS=2) as bme:
            t, h, p = bme.readForced()
            self.assertTrue(t > 0 and h > 0 and p > 0)
        with bme280.BME280(spiBus={ "sck": 21, "mosi": 22, "miso": 23 }, spiCS=2) as bme:
            t, h, p = bme.readForced()
            self.assertTrue(t > 0 and h > 0 and p > 0)
        with bme280.BME280(spiBus=machine.SPI(42, sck=21, mosi=22, miso=23), spiCS=2) as bme:
            t, h, p = bme.readForced()
            self.assertTrue(t > 0 and h > 0 and p > 0)
        with bme280.BME280(spiBus=machine.SPI(42,
                                              sck=machine.Pin(21, mode=machine.Pin.OUT, value=0),
                                              mosi=machine.Pin(22, mode=machine.Pin.OUT, value=0),
                                              miso=machine.Pin(23, mode=machine.Pin.IN)),
                           spiCS=machine.Pin(2, mode=machine.Pin.OUT, value=1)) as bme:
            t, h, p = bme.readForced()
            self.assertTrue(t > 0 and h > 0 and p > 0)

        # Test async
        async def coroutine_():
            async with bme280.BME280(spiBus=42, spiCS=2) as bme:
                t, h, p = await bme.readForcedAsync()
                self.assertTrue(t > 0 and h > 0 and p > 0)
        uasyncio.run(coroutine_())

        # Normal mode
        with bme280.BME280(spiBus=42, spiCS=2) as bme:
            bme.start(mode=bme280.MODE_NORMAL,
                      standbyTime=bme280.T_SB_10ms)

        # Other methods
        with bme280.BME280(spiBus=42, spiCS=2) as bme:
            bme.readForced()
            self.assertFalse(bme.isMeasuring())
            bme.reset()

# vim: ts=4 sw=4 expandtab
