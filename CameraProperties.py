import pickle
import numpy
from picamera import PiCamera

class CameraProperties(object):
    # camera properties
    properties = {'ISO' : [0, 100, 200, 320, 400, 500, 640, 800],
                  'Exposure Mode' : ['off', 'auto', 'night', 'nightpreview', 'backlight', 
                                     'spotlight', 'sports', 'snow', 'beach', 'verylong', 
                                     'fixedfps', 'antishake', 'fireworks'],
                  'AWB Mode' : ['off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 
                                'fluorescent', 'incandescent', 'flash', 'horizon'],
                  'AWB Red Gain' : numpy.arange(0.0, 8.0, 0.2),
                  'AWB Blue Gain' : numpy.arange(0.0, 8.0, 0.2),
                  'Exp Compensation' : range(-25, +25+1),
                  'Exp Meter Mode' : ['average', 'spot', 'matrix', 'backlit'],
                  'Brightness' : range(0, 100+1),               
                  'Contrast' : range(0, 100+1),
                  'Saturation' : range(-100, +100+1),               
                  'Sharpness' : range(-100, +100+1),
                  'Shutter Speed' : numpy.arange(1000, 60000, 1000),
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
        print('Setting %s to %s' % (name, value))
        if name == 'DRC Strength':
             self.cam.drc_strength = value
        # 'Brightness', 'ISO', 'Exp Compensation', 'Contrast', 'Saturation', 'AWB Red Gain', 'Exp Meter Mode', 'Sharpness', 'AWB Mode', 'Shutter Speed', 'Exposure Mode', 'AWB Blue Gain'
        
    def CurrentPropertyName(self):
        return list(self.properties)[self.property_index]

    def CurrentPropertyValue(self):
        name = self.CurrentPropertyName()
        return self.properties[name][self.values_indices[name]]

    def PrintAllProperties(self):
        print('*' * 16)
        for name in self.properties.keys():
            value = self.properties[name][self.values_indices[name]]
            print("%s = %s <%s>" % (name, value, self.GetProperty(name)))
        print('Exp Speed (READONLY) = %s' % (int (self.cam.exposure_speed)))
        print('*' * 16)
        
    def PrintCurrentProperty(self):
        print("%s = %s" % (self.CurrentPropertyName(), self.CurrentPropertyValue()))

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
