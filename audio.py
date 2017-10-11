import alsaaudio, time, audioop

# Open the device in nonblocking capture mode. The last argument could
# just as well have been zero for blocking mode. Then we could have
# left out the sleep call in the bottom of the loop
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)

inp.setchannels(1)
inp.setrate(8000)  # 16000
inp.setformat(alsaaudio.PCM_FORMAT_U8)  # PCM_FORMAT_S16_LE for ubuntu
inp.setperiodsize(160)

while True:
    # Read data from device
    l,data = inp.read()
    if l:
        # Return the maximum of the absolute value of all samples in a fragment.
        volume = audioop.max(data, 1) # 2 for ubuntu
        print(volume)
    time.sleep(.001)
