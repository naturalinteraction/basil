import time
import pickle

global customer
customer = 'not-set-yet'

global git_rev_count_and_branch
git_rev_count_and_branch = 'none'

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

global batch
global last_batch
global batch_start
try:
    with open('batch.pkl', 'r') as f:
        (batch, batch_start, last_batch) = pickle.load(f)
        # print('read batch 3', batch, batch_start, last_batch)
except:
    try:
        with open('batch.pkl', 'r') as f:
            (batch, batch_start) = pickle.load(f)
            last_batch = batch
            # print('read batch 2', batch, batch_start, last_batch)
    except:
        batch = ''
        last_batch = ''
        batch_start = 0
        # print('read batch 0', batch, batch_start, last_batch)

global hour_start
global hour_end
try:
    with open('hourly.pkl', 'r') as f:
        (hour_start, hour_end) = pickle.load(f)
except:
    hour_start = 8
    hour_end = 20

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
