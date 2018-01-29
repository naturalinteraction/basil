# basil

A repo for my own experiments.

#### Specs
1. Measure area with good growth and area with issues.
2. Curve of growth in time.
3. Algorithm is plant-specific. Plant in tray is known.
4. White light.
5. Substrate will guarantee good contrast.

#### High-level tasks
- [ ] Algorithms: segmentation, analysis, calibration
- [ ] Definition of architectural aspects (image storage, notifications, etc.)
- [ ] Optimization on sensor
- [ ] Design UI for management (and then implement it)
- [ ] Design enclosing case
- [ ] Hardware specification document
- [ ] Commented source code
- [ ] Documentation

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
- [x] Segmentation: model hole color and dead leaves color
- [x] Segmentation: model substrate color
- [x] Holes: consider their hierarchy
- [x] Segmentation: multi-dimensional k-means clustering as a tool
- [x] Lab, Luv, YUV color spaces
- [x] Superpixels
- [ ] Perspective mask
- [ ] Segmentation: downsizing
- [ ] Find biomass segmentation algorithm params automatically
- [ ] Segmentation: Otsu thresholding and adaptive thresholding
- [ ] Sobel, Scharr and Laplacian on these channels separately: saturation, brightness, luminance + Canny
- [ ] Textural information: spatial frequency function pixel by pixel, textons and their neighborhood histograms
- [ ] ~~Color analysis inside biomass: histograms~~
- [ ] ~~Likelihood of a pixel to belong to a class based on color and spatial location (neighborhood)~~
- [ ] ~~Holes: pixel-by-pixel~~

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
- [x] Sensor color calibration == Find camera parameters automatically
- [x] Web interface: number of images in queue
- [x] Print 24 errors (with the average squared error)
- [x] Web interface
- [ ] Compare camera properties that are a result of color calibration and auto calibration across multiple sensors. Which BF?
- [ ] Click 3-4 times instead of 24
- [ ] Search brightness and contrast values (after the gains are good)?
- [ ] ~~Further test the exposure metering modes~~
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

#### Web server on the sensors
```
pip install twisted
sudo pip install service_identity
pip install service_identity
```
The last command fails but then Twisted is happy anyway.

#### Calibrations
Initial: Needs light. Must be done every time the sensor is turned on.
Auto: Needs light + scene.
Color: Needs light + colorchecker. Can provide final error(s).
