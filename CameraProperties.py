import pickle
import numpy
from picamera import PiCamera
import socket
import time

class CameraProperties(object):
    # camera properties
    properties = {'ISO' : [0, 100, 200, 320, 400, 500, 640, 800],
                  'Exposure Mode' : ['off', 'auto', 'night', 'nightpreview', 'backlight', 
                                     'spotlight', 'sports', 'snow', 'beach', 'verylong', 
                                     'fixedfps', 'antishake', 'fireworks'],
                  'AWB Mode' : ['off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 
                                'fluorescent', 'incandescent', 'flash', 'horizon'],
                  'AWB Red Gain' : numpy.arange(0.0, 8.0, 0.1),
                  'AWB Blue Gain' : numpy.arange(0.0, 8.0, 0.1),
                  'Exp Compensation' : numpy.arange(-25, +25+1, 5),
                  'Exp Meter Mode' : ['average', 'spot', 'matrix', 'backlit'],
                  'Brightness' : numpy.arange(0, 100+1, 10),               
                  'Contrast' : numpy.arange(0, 100+1, 10),
                  'Saturation' : numpy.arange(-100, +100+1, 10),               
                  'Sharpness' : numpy.arange(-100, +100+1, 10),
                  'Shutter Speed' : numpy.arange(0, 80000, 250),
                  'DRC Strength' : ['off', 'low', 'medium', 'high']    
                 }
    # indices of the currently selected camera properties' values
    values_indices = dict(list(zip(list(properties.keys()), [0] * len(properties))))
    # index of the currently selected camera property
    property_index = 0
    cam = None
    auto_calibrate = False
    
    def __init__(self, camera):
        self.cam = camera
    
    def PropertyOnCamera(self, name):
        if name == 'DRC Strength':
             return self.cam.drc_strength
        if name == 'Brightness':
             return self.cam.brightness
        if name == 'ISO':
             return self.cam.iso
        if name == 'Exp Compensation':
             return self.cam.exposure_compensation
        if name == 'Contrast':
             return self.cam.contrast
        if name == 'AWB Red Gain':
             return float(self.cam.awb_gains[0])
        if name == 'Exp Meter Mode':
             return self.cam.meter_mode
        if name == 'Sharpness':
             return self.cam.sharpness
        if name == 'Saturation':
             return self.cam.saturation
        if name == 'AWB Mode':
             return self.cam.awb_mode
        if name == 'Shutter Speed':
             return self.cam.shutter_speed
        if name == 'Exposure Mode':
             return self.cam.exposure_mode
        if name == 'AWB Blue Gain':
             return float(self.cam.awb_gains[1])
        
    def SetPropertyOnCamera(self, name, value, mute=False):
        self.loaded_values[name] = value
        if mute == False:
            print(('Attempting to set %s to %s' % (name, value)))
        if name == 'DRC Strength':
             self.cam.drc_strength = value
        if name == 'Brightness':
             self.cam.brightness = value
        if name == 'ISO':
             self.cam.iso = value
        if name == 'Exp Compensation':
             self.cam.exposure_compensation = value
        if name == 'Contrast':
             self.cam.contrast = value
        if name == 'AWB Red Gain':
             g = list(self.cam.awb_gains)
             g[0] = value     
             self.cam.awb_gains = g
        if name == 'Exp Meter Mode':
             self.cam.meter_mode = value
        if name == 'Sharpness':
             self.cam.sharpness = value
        if name == 'Saturation':
             self.cam.saturation = value
        if name == 'AWB Mode':
             self.cam.awb_mode = value
        if name == 'Shutter Speed':
             self.cam.shutter_speed = value
        if name == 'Exposure Mode':
             self.cam.exposure_mode = value
        if name == 'AWB Blue Gain':
             g = list(self.cam.awb_gains)
             g[1] = value 
             self.cam.awb_gains = g

    def SetAllPropertiesOnCamera(self):
        for name in list(self.properties.keys()):
            value = self.loaded_values[name]
            self.SetPropertyOnCamera(name, value)
        value_r = self.loaded_values['AWB Red Gain']
        value_b = self.loaded_values['AWB Blue Gain']
        self.cam.awb_gains = (value_r, value_b)

    def SetFreakingGains(self, r, b):
        self.cam.awb_gains = (r, b)
            
    def StartStopAutoCalibration(self):
        if (self.PropertyOnCamera('ISO') != 0
        or self.PropertyOnCamera('Shutter Speed') != 0
        or self.PropertyOnCamera('AWB Mode') != 'auto'
        or self.PropertyOnCamera('Exposure Mode') != 'auto'):
            print('Setting ISO and Shutter Speed to 0. Setting Exposure Mode and AWB Mode to "auto". Wait, please.')
            self.cam.iso = 0
            self.cam.exposure_mode = 'auto'
            self.cam.awb_mode = 'auto'
            self.cam.shutter_speed = 0
            self.auto_calibrate = True
            self.cam.saturation = 0
            self.cam.brightness = 50
            self.cam.contrast = 0
            return
        self.cam.shutter_speed = self.cam.exposure_speed
        self.cam.exposure_mode = 'off'
        self.cam.shutter_speed = self.cam.exposure_speed
        g = self.cam.awb_gains
        self.cam.awb_mode = 'off'
        self.cam.awb_gains = g
        self.cam.iso = 100
        self.auto_calibrate = False
        print('Exposure Mode, ISO, Shutter Speed and AWB Mode and Gains set.')
        self.Save()
        self.Load()
        print(self.loaded_values['Shutter Speed'], self.loaded_values['AWB Red Gain'], self.loaded_values['AWB Blue Gain'])

    def CurrentPropertyName(self):
        return list(self.properties)[self.property_index]

    def CurrentPropertyValue(self):
        name = self.CurrentPropertyName()
        return self.properties[name][self.values_indices[name]]

    def PropertyValue(self, name):
        return self.properties[name][self.values_indices[name]]

    def PrintAllProperties(self):
        print(('*' * 20))
        for name in sorted(list(self.properties.keys())):
            value = self.properties[name][self.values_indices[name]]
            print(("%s  %s <%s>" % (name, value, self.PropertyOnCamera(name))))
        print(('Exp Speed (READONLY) <%s>' % (int(self.cam.exposure_speed))))
        print(('Analog Gain (READONLY) <%.3f>' % float(self.cam.analog_gain)))
        print(('Digital Gain (READONLY) <%.3f>' % float(self.cam.digital_gain)))
        zoo = self.cam.zoom
        print(('Zoom <%s, %s, %s, %s>' % (zoo[0], zoo[1], zoo[2], zoo[3])))
        print(('*' * 20))

    def AllPropertiesString(self):
        result = ''
        for name in sorted(list(self.properties.keys())):
            if 'Gain' in name:
                result = result + "%s  %.3f" % (name.replace('AWB ', ''), float(self.PropertyOnCamera(name))) + '<br>\n'
            else:
                result = result + "%s  %s" % (name, str(self.PropertyOnCamera(name))) + '<br>\n'
        result = result + 'Exp Speed %s' % (int(self.cam.exposure_speed)) + '<br>\n'
        result = result + 'Analog Gain %.3f' % float(self.cam.analog_gain) + '<br>\n'
        result = result + 'Digital Gain %.3f' % float(self.cam.digital_gain) + '<br>\n'
        zoo = self.cam.zoom
        zoomed = (zoo[2] < 1.0)
        result = result + 'Zoomed ' + str(zoomed) + '<br>\n'
        return str(result)

    def AllPropertiesOK(self):
        if float(self.PropertyOnCamera('AWB Blue Gain')) < 0.5:
            return False
        if float(self.PropertyOnCamera('AWB Red Gain')) < 0.5:
            return False
        if self.PropertyOnCamera('AWB Mode') != 'off':
            return False
        if self.PropertyOnCamera('DRC Strength') != 'off':
            return False
        if self.PropertyOnCamera('Exposure Mode') != 'off':
            return False
        if self.PropertyOnCamera('Exp Meter Mode') != 'average':
            return False
        if self.PropertyOnCamera('Exp Compensation') != 0:
            return False
        if self.PropertyOnCamera('ISO') != 100:
            return False
        if self.PropertyOnCamera('Brightness') != 50:
            return False
        if self.PropertyOnCamera('Contrast') != 0:
            return False
        if self.PropertyOnCamera('Saturation') != 0:
            return False
        if self.PropertyOnCamera('Sharpness') != 100:
            return False
        shutter_speed = self.PropertyOnCamera('Shutter Speed')
        if shutter_speed < 1500:
            return False
        if abs(int(self.cam.exposure_speed) - shutter_speed) > 200:
            return False
        if abs(1.0 - float(self.cam.analog_gain)) > 0.07:
            return False
        if abs(1.0 - float(self.cam.digital_gain)) > 0.07:
            return False
        if self.cam.zoom[2] != 1.0:
            return False
        return True

    def PrintCurrentProperty(self):
        print(("%s   %s <%s>" % (self.CurrentPropertyName(), self.CurrentPropertyValue(), self.PropertyOnCamera(self.CurrentPropertyName()))))

    def IncValue(self):
        name = self.CurrentPropertyName()
        if self.values_indices[name] < (len(self.properties[name]) - 1):
            self.values_indices[name] += 1
        self.PrintCurrentProperty()

    def DecValue(self):
        name = self.CurrentPropertyName()
        if self.values_indices[name] > 0:
            self.values_indices[name] -= 1
        self.PrintCurrentProperty()

    def IncProperty(self):
        if self.property_index < (len(self.properties) - 1):
            self.property_index += 1
        self.PrintCurrentProperty()

    def DecProperty(self):
        if self.property_index > 0:
            self.property_index -= 1
        self.PrintCurrentProperty()

    def Save(self):
        filename = 'camera-properties.pkl'
        current_values = {}
        for name in sorted(list(self.properties.keys())):
            current_values[name] = self.PropertyOnCamera(name)
        with open(filename, 'w') as f:
            pickle.dump((self.values_indices, current_values), f, 0)
        print('Saved.')

    def Load(self):
        filename = 'camera-properties.pkl'
        try:
            with open(filename, 'r') as f:
                print('camera-properties.pkl found.')
        except:
            print('loading default camera properties.')
            filename = 'default-camera-properties.pkl'
        with open(filename, 'r') as f:
            (self.values_indices,self.loaded_values) = pickle.load(f)
        print('Loaded.')
