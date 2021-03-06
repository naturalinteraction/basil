import alsaaudio, time, audioop

def AudioLevel(format):
    try:
        # Open the device in nonblocking capture mode. The last argument could
        # just as well have been zero for blocking mode. Then we could have
        # left out the sleep call in the bottom of the loop
        # print(alsaaudio.pcms())
        # print(alsaaudio.cards())
        if format == alsaaudio.PCM_FORMAT_S16_LE:  # select sound card automatically
            inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)
        else:  # select second sound card (the USB PnP microphone)
            inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK, 'whatever', 1)
        inp.setchannels(1)
        inp.setrate(8000)
        inp.setformat(format)  # PCM_FORMAT_S16_LE for laptop, PCM_FORMAT_U8 for pi
        bytes = 1    # 2 for laptop, 1 for pi
        if format == alsaaudio.PCM_FORMAT_S16_LE:
	    bytes = 2
        inp.setperiodsize(160)
        volume = 0.0
        for i in range(0, 100):
	    # Read data from device
	    l,data = inp.read()
	    if l:
	        # Return the maximum of the absolute value of all samples in a fragment.
	        volume += audioop.max(data, bytes)
	    time.sleep(0.002)
        return (int(volume * volume / 1000.0 / 1000.0 / 2))
    except:
        return -1  # probably no microphone

def AudioLevelPi():
    return AudioLevel(alsaaudio.PCM_FORMAT_U8)

def AudioLevelLaptop():
    return AudioLevel(alsaaudio.PCM_FORMAT_S16_LE)
