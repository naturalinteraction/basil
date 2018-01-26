import time

global image
image = None

global show
show = True

global color_calibrate
color_calibrate = False

global campaign
campaign = 'xxx'

global cameraproperties
cameraproperties = None

global last_picture_taken_ticks
last_picture_taken_ticks = -1

global last_picture_filename
last_picture_filename = ''

global just_started
just_started = True

global just_started_but_done
just_started_but_done = False

global gain_distance
gain_distance = -1.0

global previous_analog_gain
previous_analog_gain = -1.0

global previous_digital_gain
previous_digital_gain = -1.0

global time_process_started
time_process_started = time.time()

global time_process_started_string
time_process_started_string = time.strftime("%Y/%m/%d %H:%M")

global locations
locations = []
