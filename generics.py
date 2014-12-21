
class GenericType(type): pass
    
A = type('A', (GenericType,), {})
B = type('B', (GenericType,), {})
C = type('C', (GenericType,), {})
D = type('D', (GenericType,), {})
