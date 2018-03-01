import time
import pickle

global image
image = None

global show
show = True

global color_calibrate
color_calibrate = False

global calib_error
calib_error = '0'

global should_quit
should_quit = False

global should_restart
should_restart = False

global should_reboot
should_reboot = False

global start_color_calibration
start_color_calibration = False

global series
# series = 'series-name'
# with open('series.pkl', 'w') as f:
#     pickle.dump(series, f, 0)
with open('series.pkl', 'r') as f:
    series = str(pickle.load(f))
# print('series', series)

global cameraproperties
cameraproperties = None

global last_picture_taken_ticks
last_picture_taken_ticks = -1

global last_picture_filename
last_picture_filename = ''

global initial_calibrate
initial_calibrate = True

global initial_calibrate_but_done
initial_calibrate_but_done = False

global gain_diff
gain_diff = -1.0

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
