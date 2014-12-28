from itertools import izip
from generics import is_generic
from function import Function

gen_name = lambda cls, ts: '%s[%s]' % (cls.__name__, [t.__name__ for t in ts])

# Trait
class TraitT(type):
    def __getitem__(cls, ts):
        """
        Implements a class of Trait with provided shape: Trait[A]
        """
        ts = ts if isinstance(ts, tuple) else (ts,)

        assert all(is_generic(t) for t in ts)

        return TraitAbsT(gen_name(cls, ts), (TraitAbs, cls,), {
            '__types__': ts
        })

class TraitAbsT(TraitT):
    def __getitem__(cls, ts):
        """
        Implementation of a generic trait:

        class Bar(Foo[int]): pass

        """
        ts = ts if isinstance(ts, tuple) else (ts,)
        assert all(isinstance(t, type) for t in ts)
        assert len(ts) == len(cls.__types__)

        # Resolve types!
        gen_map = {T: t for T, t in izip(cls.__types__, ts) if is_generic(T)}
        
        return TraitImplT(gen_name(cls, ts), (TraitImpl, cls,), {
            '__typemap__': gen_map
        })

def get_typemap(attrs, bases):
    """bfs"""
    s = list(bases)
    seen = set(s)
    it = iter(s)
    while True:
        if '__typemap__' in attrs:
            return attrs['__typemap__']

        next_base = next(it, None)
        assert next_base is not None

        s.extend(b for b in next_base.__bases__ if b not in seen)
        seen.update(next_base.__bases__)
        attrs = next_base.__dict__

class TraitImplT(TraitAbsT):
    def __new__(cls, name, bases, attrs):
        # Resolve each function with their types
        new_attrs = {}
        ts = get_typemap(attrs, bases)
        for k, v in attrs.iteritems():
            if isinstance(v, Function):
                r_gens = [ts.get(t, t) for t in v.generics]
                v = v[tuple(r_gens)]

            new_attrs[k] = v

        new_attrs['__metaclass__'] = type

        new_cls = type.__new__(cls, name, bases, new_attrs)
        return new_cls

class Trait(object):
    __metaclass__ = TraitT

class TraitAbs(object):
    __metaclass__ = TraitAbsT

class TraitImpl(object):
    __metaclass__ = TraitAbsT
