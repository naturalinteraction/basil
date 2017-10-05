class CameraProperties(object):
    # camera properties
    properties = {'ISO' : [100, 200],
                  'Exposure Mode' : ['off', 'auto', 'night'],
                  'Exposure Compensation' : range(-25, +25+1)
                 }
    # indices of the currently selected camera properties' values
    values_indices = dict(zip(properties.keys(), [0] * len(properties)))
    # index of the currently selected camera property
    property_index = 0

    def CurrentPropertyName(self):
        return list(self.properties)[self.property_index]

    def CurrentPropertyValue(self):
        name = self.CurrentPropertyName()
        return self.properties[name][self.values_indices[name]]

    def IncIndex(self):
        if self.property_index < (len(self.properties) - 1):
            self.property_index += 1

    def PrintProperty(self):
        print(self.CurrentPropertyName(), ' is ', self.CurrentPropertyValue())    

cp = CameraProperties()
cp.PrintProperty()
cp.IncIndex()
cp.PrintProperty()
#cp.property_index = cp.IncIndex(cp.property_index, cp.properties)
cp.PrintProperty()
