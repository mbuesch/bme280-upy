#!/usr/bin/env python3

from setuptools import setup
import sys, os

basedir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(basedir, "README.md"), "rb") as fd:
    readmeText = fd.read().decode("UTF-8")

setup(
    name="bme280-upy",
    version="2.0.0",
    description="BME-280 sensor device driver with Micropython and Linux support (I2C + SPI)",
    license="GNU General Public License v2 or later",
    author="Michael Büsch",
    author_email="m@bues.ch",
    url="https://bues.ch/",
    packages=["bme280"],
    keywords = "Micropython BME280 SPI I2C Raspberry-Pi",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: MicroPython",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
    long_description=readmeText,
    long_description_content_type="text/markdown",
)

# vim: ts=4 sw=4 expandtab
