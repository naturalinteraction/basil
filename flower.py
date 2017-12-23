# Read data from Flower Care, tested on firmware version 2.7.0

# 1)  sudo hcitool lescan
# 2)  sudo python flower.py C4:7C:8D:65:C9:87

# Battery level: 100 %
# Firmware version: 2.7.0
# Light intensity: 47 lux
# Temperature: 19.1 C
# Soil moisture: 0 %
# Soil fertility: 0 uS/cm

import sys
from gattlib import GATTRequester, GATTResponse
from struct import *

address = sys.argv[1]
requester = GATTRequester(address)
# Read battery and firmware version attribute
data=requester.read_by_handle(0x0038)[0]
battery, version = unpack('<B6s',data)
print "Battery level:",battery,"%"
print "Firmware version:",version
# Enable real-time data reading
requester.write_by_handle(0x0033, str(bytearray([0xa0, 0x1f])))
# Read plant data
data=requester.read_by_handle(0x0035)[0]
temperature, sunlight, moisture, fertility = unpack('<hxIBHxxxxxx',data)
print "Light intensity:",sunlight,"lux"
print "Temperature:",temperature/10.,"C"
print "Soil moisture:",moisture,"%"
print "Soil fertility:",fertility,"uS/cm"
