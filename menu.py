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

    def IncIndex(self, ind, lis):
        if ind < (len(lis) - 1):
            ind += 1
        return ind

    def PrintProperty(self):
        print(self.CurrentPropertyName(), ' is ', self.CurrentPropertyValue())    

cp = CameraProperties()
cp.PrintProperty()
cp.property_index = cp.IncIndex(cp.property_index, cp.properties)
cp.PrintProperty()
cp.property_index = cp.IncIndex(cp.property_index, cp.properties)
cp.PrintProperty()
