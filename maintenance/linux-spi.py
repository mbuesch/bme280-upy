#!/usr/bin/env python3

import bme280
import sys
import time

if len(sys.argv) >= 3:
    spiBus = int(sys.argv[1])
    spiCS = int(sys.argv[2])
else:
    spiBus = 0
    spiCS = 0

with bme280.BME280(spiBus=spiBus, spiCS=spiCS) as bme:
    while True:
        t, h, p = bme.readForced(filter=bme280.FILTER_4,
                                 tempOversampling=bme280.OVSMPL_4,
                                 humidityOversampling=bme280.OVSMPL_16,
                                 pressureOversampling=bme280.OVSMPL_4)
        print("t=%.2f  h=%.2f  p=%.1f" % (t, h * 1e2, p * 1e-2))
        time.sleep(0.5)

# vim: ts=4 sw=4 expandtab
