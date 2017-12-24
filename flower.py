# Read data from Flower Care, tested on firmware version 2.7.0

# sudo apt-get install libbluetooth-dev
# sudo apt-get install libboost-python-dev
# sudo apt-get install libboost-all-dev
# pip install gattlib

# 1)  sudo hcitool lescan
# 2)  sudo python flower.py C4:7C:8D:65:C9:87

# Battery level: 100 %
# Firmware version: 2.7.0
# Light intensity: 47 lux
# Temperature: 19.1 C
# Soil moisture: 0 %
# Soil fertility: 0 uS/cm

import sys
import string
from gattlib import GATTRequester, GATTResponse
from struct import *

def ReadFlowerCare(address):
  try:
    requester = GATTRequester(address)
  except:
    return 'error', 0, 0, 0, 0, 0
  try:
    # Read battery and firmware version attribute
    data = requester.read_by_handle(0x0038)[0]
    battery, version = unpack('<B6s',data)
    version = filter(lambda x : x in string.printable, version)
  except:
    return 'error', 0, 0, 0, 0, 0
  try:
    # Enable real-time data reading
    requester.write_by_handle(0x0033, str(bytearray([0xa0, 0x1f])))
  except:
    return 'error', 0, 0, 0, 0, 0
  try:
    # Read plant data
    data = requester.read_by_handle(0x0035)[0]
  except:
    return 'error', 0, 0, 0, 0, 0
  try:
    temperature, sunlight, moisture, fertility = unpack('<hxIBHxxxxxx', data)
    return version, battery, temperature, sunlight, moisture, fertility
  except:
    return 'error', 0, 0, 0, 0, 0

address = sys.argv[1]

version, battery, temperature, sunlight, moisture, fertility = ReadFlowerCare(address)

if version != 'error':
  print("Firmware version: " + version)
  print("Battery level: " + str(battery) + "%")
  print("Light intensity: " + str(sunlight) + "lux (> 1000 lux)")
  print("Temperature: " + str(temperature / 10.0) + "C (17C - 26C)")
  print("Soil moisture: " + str(moisture) + "% (35% - 90%)")
  print("Soil fertility: " + str(fertility) + "uS/cm (200 uS/cm - 1200 uS/cm)")
else:
  print('error!')
