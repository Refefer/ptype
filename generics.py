from itertools import izip

class GenericType(type): pass
    
A = type('A', (GenericType,), {})
B = type('B', (GenericType,), {})
C = type('C', (GenericType,), {})
D = type('D', (GenericType,), {})

is_generic = lambda t: issubclass(t, GenericType)

