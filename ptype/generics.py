
class GenericType(type): pass
    
A = type('A', (GenericType,), {})
B = type('B', (GenericType,), {})
C = type('C', (GenericType,), {})
D = type('D', (GenericType,), {})

def is_generic(t):
    if isinstance(t, type) and issubclass(t, GenericType):
        return True

    return isinstance(t, ImpT) and len(t.get_generics()) > 0

class ImpT(object):
    def resolve(self, generics_map):
        raise NotImplementedError()

    def get(self):
        raise NotImplementedError()

    def get_generics(self):
        return []

    @property
    def __name__(self):
        raise NotImplementedError()
