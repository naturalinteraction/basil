# basil

A repo for my own experiments.


#### Tasks dip.py

- [x] List all pictures on S3
- [x] Check if local file exists
- [x] Download pictures that are not here yet
- [x] Group images with the same 'note' and campaign identifier
- [x] Open downloaded images
- [x] Cython threshold function
- [x] Optionally download images from S3
- [x] Display multiple images with the discarded areas, for debugging purposes
- [x] Stable biomass bounding box (also useful for cropping)
- [x] Unit tests, integration tests
- [x] Modularize the image processing pipeline
- [x] Test median blur and blur
- [ ] Consider not only holes but all peripheral regions, pixel-by-pixel
- [ ] Color analysis inside biomass: histograms
- [ ] Sobel, Scharr and Laplacian on all channels separately: B, G, R, H, S, V, luminance
- [ ] Find biomass segmentation algorithm params automatically
- [ ] ~~Test CV_BGR2Lab~~

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
- [x] Remove all uses of 'global'
- [x] Unzoom when taking picture
- [x] Disable preview automatically (when taking picture)
- [x] Start cap.py at boot
- [x] Update git repo, relaunch cap.py, reboot and shutdown remotely via script on the 4 sensors at once
- [x] Integrate microphone
- [ ] Test more the exposure metering modes
- [ ] Sensor color calibration
- [ ] Find camera parameters automatically
- [ ] ~~Possibly freeze awb but not iso, expo, shutter~~
- [ ] ~~Camera on/off (250mA, no continuous mode)~~
- [ ] ~~Detect if scene is not static~~
- [ ] ~~Detect if scene is dark~~


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
sshpass -p ********* ssh pi@192.168.1.10 'cd /home/pi/basil ; git pull ; sudo /sbin/shutdown now'
```


#### Sensors
```
blueshift	eth: 192.168.0.6	wifi: DHCP	Pi NoIR Camera V2
redshift	eth: 192.168.0.7	wifi: DHCP	Pi NoIR Camera V2
noir		eth: 192.168.0.8	wifi: DHCP	Pi NoIR Camera V2
visible		eth: 192.168.0.9	wifi: DHCP	Pi Camera Module V2
```
Focus set at 350mm. Ended tests on optical filters on Dec 17th. Since that date, despite the hostname, the difference is just the camera sensor.

To look for local raspberries:
```
sudo nmap -sP 192.168.1.0/24 | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}'
```


#### Autostart
Append `@/home/pi/basil/autostart.sh` to `/home/pi/.config/lxsession/LXDE-pi/autostart`


#### Timelapse
```
# 7 fps, other options include hd720, hd480
ffmpeg -r 7 -pattern_type glob -i '*.jpeg' -s hd1080 -vcodec libx264 timelapse.mp4

# with crop w:h:x:y
ffmpeg -r 7 -pattern_type glob -i '*.jpeg' -s hd1080 -vcodec libx264 -filter:v "crop=1050:871:857:776" timelapse.mp4
```


#### Exif Keywords
```
exiftool -keywords <filename>
```

#### Git
Save username and password for 4 months:
```
git config --global credential.helper 'cache --timeout=10000000'
```
