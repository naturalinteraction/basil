# basil

A repo for my own experiments.


#### Tasks dip.py

- [ ] List all pictures on S3
- [ ] Check if file exists with import os.path and os.path.isfile(filename)
- [ ] Download pictures that are not here yet
- [ ] Group images that start with the same 'note'
- [ ] Open downloaded images
- [ ] Examine timelapses

#### Tasks cap.py

- [x] Set shutter speed
- [x] Print all camera properties
- [x] Save/Load camera properties
- [x] Arrow keys select property and change its value
- [x] Get/Set camera property value by name
- [x] Set optimal camera properties programmatically
- [x] Preview on/off
- [x] Save image locally, timely
- [x] Include resolution and notes in filenames
- [x] Alternatively show a full resolution image (useful for focusing) or just a convenient thumbnail
- [x] Add uptime to EXIF
- [x] Add source code version to EXIF
- [x] Print source code version when TAB is pressed
- [x] Print date and time the process started (plus uptime) when TAB is pressed
- [x] Add all camera properties to EXIF
- [x] Determine best resolution for both camera versions
- [x] Manage network failures (upload queue)
- [x] Upload image to S3
- [x] Decide whether to use same resolution for both models
- [x] Detect camera hardware version
- [x] Detect camera presence
- [ ] Update git repo, start and stop cap.py, reboot and shutdown remotely via script on the 4 sensors at once
- [ ] Start cap.py at boot
- [ ] ~~Camera on/off (250mA, no continuous mode)~~
- [ ] ~~Detect if scene is static~~

#### Creating image of SD card:
```
sudo dd if=/dev/mmcblk0 of=sdimage.img bs=4096 conv=notrunc
```

#### Copying image to SD card:
```
sudo dd if=sdimage.img of=/dev/mmcblk0 bs=4096 conv=notrunc
```

#### Checking `dd` progress:
```
sudo kill -USR1 $(pgrep ^dd)
```

#### VNC for Chrome:
<https://chrome.google.com/webstore/detail/vnc®-viewer-for-google-ch/iabmpiboiopbgfabjmgeedhcmjenhbla>


#### Mount Pi:
```
sshfs pi@or**.ddns.net:basil pi
```

#### Unmount Pi:
```
fusermount -u pi
```

#### Password
```
sshpass -p ********* ssh pi@or**.ddns.net 'bash -s' < do.sh
sshpass -p ********* ssh pi@192.168.0.9 'cd /home/pi/basil ; git pull ; sudo /sbin/shutdown now'
```

#### Sensors
```
blueshift	wifi: 192.168.0.6	eth: DHCP
redshift	wifi: 192.168.0.7	eth: DHCP
noir		wifi: 192.168.0.8	eth: DHCP
visible		wifi: 192.168.0.9	eth: DHCP
```
Focus set at 350mm.

#### Autostart
Append `@/home/pi/basil/autostart.sh` to `/home/pi/.config/lxsession/LXDE-pi/autostart`
