from generics import is_generic
from function import Function

gen_name = lambda cls, ts: '%s[%s]' % (cls.__name__, [t.__name__ for t in ts])

# Trait
class TraitT(type):
    def __getitem__(cls, ts):
        """
        Implements a class of Trait with provided shape
        """
        ts = ts if isinstance(ts, tuple) else (ts,)
        assert all(isinstance(t, type) for t in ts)

        return type(gen_name(cls, ts), (cls,), {
            '__metaclass__': TraitAbsT,
            '__types__': ts
        })

class TraitAbsT(type):
    def __getitem__(cls, ts):
        ts = ts if isinstance(ts, tuple) else (ts,)
        assert all(isinstance(t, type) for t in ts)
        assert len(ts) == len(cls.__types__)

        # Resolve types!
        gen_map = {T: t for T, t in izip(cls.__types__, ts) if is_generic(T)}
        
        return type(gen_name(cls, ts), (cls,), {
            '__metaclass__': TraitImplT,
            '__typemap__': gen_map
        })

class TraitImplT(type):
    def __new__(cls, name, bases, attrs):
        # Resolve each function with their types
        new_attrs = {}
        ts = attrs['__typemap__']
        for k, v in attrs.iteritems():
            if isinstance(v, Function):
                r_gens = [ts.get(t, t) for t in v.generics]
                print v, r_gens
                v = Function[tuple(r_gens)]

            new_attrs[k] = v

        return super(TraitImplT, cls).__new__(cls, name, bases, new_attrs)

class Trait(object):
    __metaclass__ = TraitT

