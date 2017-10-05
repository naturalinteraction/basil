import pickle

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

    def PrintAllProperties(self):
        for name in self.properties.keys():
            value = self.properties[name][self.values_indices[name]]
            print("%s = %s" % (name, value))

    def PrintCurrentProperty(self):
        print("%s = %s" % (self.CurrentPropertyName(), self.CurrentPropertyValue()))

    def IncValue(self):
        name = self.CurrentPropertyName()
        if self.values_indices[name] < (len(self.properties[name]) - 1):
            self.values_indices[name] += 1

    def DecValue(self):
        name = self.CurrentPropertyName()
        if self.values_indices[name] > 0:
            self.values_indices[name] -= 1

    def IncProperty(self):
        if self.property_index < (len(self.properties) - 1):
            self.property_index += 1

    def DecProperty(self):
        if self.property_index > 0:
            self.property_index -= 1

    def Save(self):
        with open('camera-properties.pkl', 'wb') as f:
            pickle.dump(self.values_indices, f, 0)

    def Load(self):
        with open('camera-properties.pkl', 'rb') as f:
            self.values_indices = pickle.load(f)

if True:
    cp = CameraProperties ()
    print(cp.values_indices) 
    cp.PrintCurrentProperty()
    cp.Load()
    print(cp.values_indices) 
    cp.IncProperty()
    cp.PrintCurrentProperty()
    cp.IncProperty()
    cp.PrintCurrentProperty()
    for n in range(0, 100):
        cp.IncValue()
    cp.IncProperty()
    cp.PrintCurrentProperty()
    cp.DecValue()
    cp.PrintCurrentProperty()
    cp.DecProperty()
    cp.PrintCurrentProperty()
    cp.IncValue()
    cp.PrintCurrentProperty()
    print(cp.values_indices) 
    cp.Save()
    cp.PrintCurrentProperty()
    print(cp.values_indices) 
    print(cp.values_indices) 
    cp.PrintAllProperties()