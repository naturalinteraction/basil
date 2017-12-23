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

address = sys.argv[1]
requester = GATTRequester(address)
# Read battery and firmware version attribute
data = requester.read_by_handle(0x0038)[0]
battery, version = unpack('<B6s',data)
version = filter(lambda x : x in string.printable, version)
print "Battery level:",battery,"%"
print "Firmware version:",version
# Enable real-time data reading
requester.write_by_handle(0x0033, str(bytearray([0xa0, 0x1f])))
# Read plant data
data = requester.read_by_handle(0x0035)[0]
temperature, sunlight, moisture, fertility = unpack('<hxIBHxxxxxx',data)
print "Light intensity:",sunlight,"lux (> 1000 lux)"
print "Temperature:",temperature/10.,"C (17C - 26C)"
print "Soil moisture:",moisture,"% (35% - 90%)"
print "Soil fertility:",fertility,"uS/cm (200 uS/cm - 1200 uS/cm)"
