#!/usr/bin/env python
import sys
import time
import select
import numpy
import xwiimote

def dev_is_balanceboard(dev):
    time.sleep(2) # if we check the devtype to early it is reported as 'unknown' :(
    iface = xwiimote.iface(dev)
    return iface.get_devtype() == 'balanceboard'

def wait_for_balanceboard():
    print("Waiting for balanceboard to connect...")
    mon = xwiimote.monitor(True, False)
    dev = None
    while True:
        mon.get_fd(True) # blocks
        connected = mon.poll()
        if connected == None:
            continue
        elif dev_is_balanceboard(connected):
            print("Found balanceboard:", connected)
            dev = connected
            break
        else:
            # print("Found non-balanceboard device:", connected)
            # print("Waiting..")
            pass
    return dev

def measurements(iface):
    p = select.epoll.fromfd(iface.get_fd())
    while True:
        p.poll() # blocks
        event = xwiimote.event()
        iface.dispatch(event)
        tl = event.get_abs(2)[0]
        tr = event.get_abs(0)[0]
        bl = event.get_abs(3)[0]
        br = event.get_abs(1)[0]
        yield (tl,tr,bl,br)


device = wait_for_balanceboard()
iface = xwiimote.iface(device)
iface.open(xwiimote.IFACE_BALANCE_BOARD)
try:
    for m in measurements(iface):
        print('topleft%.2f'      % (float(m[0]) / 100.0) + 
              ' topright%.2f'    % (float(m[1]) / 100.0) + 
              ' bottomleft%.2f'  % (float(m[2]) / 100.0) + 
              ' bottomright%.2f' % (float(m[3]) / 100.0))
except KeyboardInterrupt:
    print("Bye!")
