#!/usr/bin/python

from utility import *

print('eth0', GetMAC('eth0'))
print('wlan0', GetMAC('wlan0'))
print('usb0', GetMAC('usb0'))
print('cpuserial', GetCPUSerial())
print('sdserial', GetSDSerial())
print('sdcid', GetSDCID())

