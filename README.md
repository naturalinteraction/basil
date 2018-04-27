# basil

![basil logo](website/logo.png)

Software for sensor devices.

#### Requirements

- Measure uniformity of growth.
- Provide curve of growth in time.

#### Specifications

- Algorithm is plant-specific.
- Plant in tray is known.
- Measurements across different plant species are not comparable.
- Day of growth is known. Starting day and hour must be known.
- White, constant light.
- Substrate is white or black and plastic.
- Distance and angle are fixed.

#### High-level tasks

- [x] Definition of architectural aspects (image storage, JSON, etc.)
- [x] Design enclosing case
- [x] Hardware specification document
- [x] Design and implement controls on web interface
- [x] Algorithms: segmentation, analysis, calibration
- [ ] Commented source code
- [ ] Operation guide

#### Architectural specs

Algorithms need to know (HTTP GET):
- (a) Unique identifier for the specific crop/tray (to link current processing with previous history)
- (b) Day of growth (0, 1, 2...) - can be calculated since a new (a) is provided
- (c) The recipe or plant kind (can be provided when a new (a) is provided, and it is bound to it)

Single Python 2.7 function for both uploads:
```
def UploadData(image_filename, json_string)  -->  True|False (whether both succeeded)
```

#### Customizing each SD image

Keep record of these (info.sh):
- SD serial
- SD cid
- Pi serial
- eth0 MAC address
- usb0 MAC address
- wlan0 MAC address

Username is the default. Password is the same everywhere. DHCP on usb0, eth0 and wlan0.

Change via script:
- Hostname / hosts file (change_hostname.sh)
- Wifi SSID and password (wifi.py)

#### Tasks dip.py

- [x] List all pictures on S3
- [x] Check if local file exists
- [x] Download pictures that are not here yet
- [x] Group images with the same hostname and batch identifier
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
- [x] Probability map instead of binary mask: likelihood of a pixel to belong to a class based on color and spatial location (neighborhood); blur to diffuse probability
- [x] Find biomass dominant tone based on saturation
- [x] Detect if scene is dark
- [x] Hires image and charts
- [x] Find biomass segmentation algorithm params automatically
- [x] Upload MQTT
- [x] Detect if scene is not static (motion detection)
- [x] Substrate-based uniformity algorithm
- [x] Store custom customer name
- [x] DrawSmoothChart() and DrawChart() do not draw phantom point at time zero
- [x] Series --> batch
- [x] MQTT only for customer zero
- [x] Limit spline propagation experimented in branch spline-parts-and-spline-until-break
- [x] Hours of operation shown and set on web interface, per sensor
- [x] Plant species and customer as dip.py argument (in batch name)
- [x] Use batch_species and legacy functions to select special algorithms
- [x] Web chart: variable ticks, fixed 15 days period
- [x] Download no longer downloads also .csv files
- [x] Make upload of csv optional
- [x] Web output of processing (local network and Internet)
- [x] List and link all available sensors and batches (including previous) *.csv for one customer (page accessible to customer)
- [ ] Set focus and set view: how?
- [ ] Need to create group subdir under downloaded/
- [ ] Directories prior/, downloaded/, timelapse/, website/CSV/ and possibly other dirs need customer string
- [ ] Make sure URLs cannot be inferred
- [ ] Generalize scripts (pull4, etc.)
- [ ] Create image of generic sensor and script(s) to customize it
- [ ] Accounts and sensors in CSVs on S3 (add, remove, list scripts): they include hostname and URLs
- [ ] ~~Link chart back to control panel~~
- [ ] ~~A big chunk of zero.py (batch_start, minutes...) is general and should be taken out~~
- [ ] ~~Send mail notifications~~
- [ ] ~~Default, generic routine with just motion and brightness (to replace RoutineDisplay as default)~~
- [ ] ~~Possible issue: Download from S3 error 'The read operation timed out'~~
- [ ] ~~Possible issue: browser caches local csv file and does not update it even when refreshing~~
- [ ] ~~Web chart: add URL parameter to highlight a specific moment~~
- [ ] ~~Thumbnail size can be specified in URL (useful on local network)~~
- [ ] ~~Comparison with average species curves~~
- [ ] ~~Store all frames on sensor until end of batch (useful for processing on sensor)~~
- [ ] ~~Create summary timeline with thumbnails~~
- [ ] ~~Control panel and chart in same web page~~
- [ ] ~~'Ping' via HTTP request~~
- [ ] ~~Buttons~~
- [ ] ~~Make console log available on the web~~
- [ ] ~~Check valid hours; always on mode if scene is lit~~
- [ ] ~~Avoid full csv URL in chart URL~~
- [ ] ~~Image processing on sensor~~
- [ ] ~~Optionally create and upload timelapse with or without superimposed graphics, but only if there is at least one more frame processed~~
- [ ] ~~Windowless cap and dip (windowed is a command line option)~~
- [ ] ~~Obfuscation and separate git repo or other delivery method~~
- [ ] ~~Get rid of set basil vars script~~
- [ ] ~~Hardware check based on MAC addresses and serials (see info.sh)~~
- [ ] ~~Background subtraction~~
- [ ] ~~Perspective warping for perspective invariant areas~~
- [ ] ~~Servers list in git: an http request containing image name is done by cap.py until a server responds positively (web server in dip.py, or calling dip.py)~~
- [ ] ~~Prior knowledge is stored somewhere~~
- [ ] ~~Mask~~
- [ ] ~~Textural information: spatial frequency function pixel by pixel, textons and their neighborhood histograms; Sobel, Scharr and Laplacian on these channels separately: saturation, brightness, luminance + Canny (blurred)~~
- [ ] ~~Retain pixel probability from previous frames (running average)~~
- [ ] ~~Segmentation: Otsu thresholding and adaptive thresholding~~
- [ ] ~~Color analysis inside biomass: histograms~~
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
- [x] Click 4 times instead of 24, perspective grid
- [x] Store date and time of crop start
- [ ] ~~Send sensor health warning (if something is wrong among cpu, memory, disk, temperature, camera properties, calibration...)~~
- [ ] ~~Compare camera properties that are a result of color calibration and auto calibration across multiple sensors. Which BF? It seems like shutter speed should be at least 5000. Probably find some custom target RGB values with new colorcheckers.~~
- [ ] ~~Search brightness and contrast values (after the gains are good). Or make sure brightness is 50 and contrast is 10 and so on.~~
- [ ] ~~Further test the exposure metering modes~~
- [ ] ~~Possibly freeze awb but not iso, expo, shutter~~
- [ ] ~~Camera on/off (250mA, no continuous mode)~~


#### Creating image of SD card:
```
# lsblk to list devices
# partition(s) must be unmounted (with umount; partitions, not the disk itself)
sudo dd if=/dev/mmcblk0 of=sdimage.img bs=4096 conv=notrunc  # if=/dev/sdb bs=4M
```


#### Copying image to SD card:
```
# lsblk to list devices
# partition(s) must be unmounted (with umount; partitions, not the disk itself)
# be very careful with what follows, see https://www.raspberrypi.org/documentation/installation/installing-images/linux.md
sudo dd if=sdimage.img of=/dev/mmcblk0 bs=4096 conv=notrunc  # of=/dev/sdb bs=4M
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

Resolution set to 1280x720 (16:9)

There is no way we can use the Raspberry Pi Zero because sourcing is unreliable.

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

#### Cython, Scipy, FFmpeg and MQTT
```
pip install Cython
sudo apt-get install python-scipy
pip install paho-mqtt
sudo apt-get install ffmpeg
```

#### Web server on the sensors
```
pip install twisted
sudo pip install service_identity
pip install service_identity
```
The last command fails but then Twisted is happy anyway.

#### Calibrations
- Initial: Needs light. Must be done every time the sensor is turned on.
- Auto: Needs light + scene.
- Color: Needs light + colorchecker. Can provide final error(s).

#### Disable HDMI
Edit `/etc/rc.local` and add the following lines above `exit 0`:
```
# Disable HDMI
/usr/bin/tvservice -o
```
Other interesting settings in `/boot/config.txt`.

#### Ignore changes to file
```
git update-index --assume-unchanged FILE
```
Must be executed on each machine. That means this is part of the installation process.
