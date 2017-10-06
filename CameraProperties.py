import pickle
import numpy
from picamera import PiCamera

# unused:
#    camera.zoom  # (x, y, w, h) not interesting at the moment
#    float(camera.analog_gain) # READONLY
#    float(camera.digital_gain) # READONLY

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
                  'Shutter Speed' : numpy.arange(0, 80000, 5000),
                  'DRC Strength' : ['off', 'low', 'medium', 'high']    
                 }
    # indices of the currently selected camera properties' values
    values_indices = dict(zip(properties.keys(), [0] * len(properties)))
    # index of the currently selected camera property
    property_index = 0
    cam = None
    
    def __init__(self, camera):
        self.cam = camera
    
    def GetProperty(self, name):
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
        
    def SetProperty(self, name, value):
        print('Attempting to set %s to %s' % (name, value))
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
    
    def FreezeExposureAWB(self):
        if self.GetProperty('ISO') == 0:
            print('Set ISO to a non-zero value first. Doing nothing.')
            return
        self.cam.shutter_speed = self.cam.exposure_speed
        self.cam.exposure_mode = 'off'
        g = self.cam.awb_gains
        self.cam.awb_mode = 'off'
        self.cam.awb_gains = g
        print('Exposure and AWB frozen.')

    def CurrentPropertyName(self):
        return list(self.properties)[self.property_index]

    def CurrentPropertyValue(self):
        name = self.CurrentPropertyName()
        return self.properties[name][self.values_indices[name]]

    def PrintAllProperties(self):
        print('*' * 20)
        for name in self.properties.keys():
            value = self.properties[name][self.values_indices[name]]
            print("%s = %s <%s>" % (name, value, self.GetProperty(name)))
        print('Exp Speed (READONLY) <%s>' % (int (self.cam.exposure_speed)))
        print('*' * 20)
        
    def PrintCurrentProperty(self):
        print("%s = %s <%s>" % (self.CurrentPropertyName(), self.CurrentPropertyValue(), self.GetProperty(self.CurrentPropertyName())))

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
        with open('camera-properties.pkl', 'wb') as f:
            pickle.dump(self.values_indices, f, 0)
        print('Saved.')

    def Load(self):
        with open('camera-properties.pkl', 'rb') as f:
            self.values_indices = pickle.load(f)
        print('Loaded.')
