#!/usr/bin/python

import sys

if len(sys.argv) != 4:
    print('usage: ./wifi.py SSID PASSWORD KEY_MGMT=[yes|no]')
    quit()

print('network={')
print('	   ssid="%s"' % sys.argv[1])
print('	   psk="%s"' % sys.argv[2])
if sys.argv[3] == 'yes':
    print('	   key_mgmt=WPA-PSK')
print('        }')

print('\n\n(append to /etc/wpa_supplicant/wpa_supplicant.conf)')
