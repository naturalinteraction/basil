# camera properties
properties = {'ISO' : [100, 200],
              'Exposure Mode' : ['off', 'auto', 'night'],
              'Exposure Compensation' : range(-25, +25+1)
             }

# indices of the currently selected camera properties' values
values_indices = dict(zip(properties.keys(), [0] * len(properties)))

# index of the currently selected camera property
property_index = 0

def CurrentPropertyName():
    return list(properties)[property_index]

def CurrentPropertyValue():
    name = CurrentPropertyName()
    return properties[name][values_indices[name]]

print(CurrentPropertyName())
property_index += 1
print(CurrentPropertyName(), ' is ', CurrentPropertyValue())

