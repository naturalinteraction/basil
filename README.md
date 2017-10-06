# basil

A repo for my own experiments.


## Tasks

- [x] Set shutter speed
- [x] Print all camera properties
- [x] Save/Load camera properties
- [x] Arrow keys select property and change its value
- [x] Get/Set camera property value by name
- [ ] Set optimal camera properties programmatically
- [ ] Preview on/off
- [ ] Determine best resolution for both camera versions (set focus and take multiple test pics)
- [ ] Decide whether to use same resolution for both models
- [ ] Save image locally
- [ ] Manage network failures (upload queue)
- [ ] Upload image to S3
- [ ] ~~Detect camera hardware version (trying to set highest resolution?)~~
- [ ] ~~Detect camera presence~~
- [ ] ~~Camera on/off (250mA, no continuous mode)~~
- [ ] ~~Detect if scene is static~~

## Creating image of SD card:
```
sudo dd if=/dev/mmcblk0 of=sdimage.img bs=4096 conv=notrunc
```

## Copying image to SD card:
```
sudo dd if=sdimage.img of=/dev/mmcblk0 bs=4096 conv=notrunc
```

## Checking `dd` progress:
```
sudo kill -USR1 $(pgrep ^dd)
```





