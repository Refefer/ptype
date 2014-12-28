from itertools import izip
from generics import is_generic
from function import Function, is_polymorphic

gen_name = lambda cls, ts: '%s[%s]' % (cls.__name__, ','.join([t.__name__ for t in ts]))

TRAIT_T_CACHE = {}

# Trait
class TraitT(type):
    def __getitem__(cls, ts):
        """
        Implements a class of Trait with provided shape: Trait[A]
        """
        ts = ts if isinstance(ts, tuple) else (ts,)

        if (cls, ts) not in TRAIT_T_CACHE:

            assert all(is_generic(t) for t in ts)

            new_t = TraitAbsT(gen_name(cls, ts), (cls,TraitAbs), {
                '__types__': ts
            })
            TRAIT_T_CACHE[(cls, ts)] = new_t

        return TRAIT_T_CACHE[(cls, ts)]

TRAIT_ABS_CACHE = {}

class TraitAbsT(TraitT):
    def __new__(cls, name, bases, attrs):
        types = get_attr(attrs, bases, '__types__') or {}
        interface = {k: v for k,v in attrs.iteritems() 
                if is_polymorphic(v, types)}
        interface.update(get_attr(attrs, bases, '__interface__') or {})
        attrs['__interface__'] = interface
        return super(cls, TraitAbsT).__new__(cls, name, bases, attrs)

    def __getitem__(cls, ts):
        """
        Implementation of a generic trait:

        class Bar(Foo[int]): pass

        """
        ts = ts if isinstance(ts, tuple) else (ts,)
        if (cls, ts) not in TRAIT_ABS_CACHE:
            assert all(isinstance(t, type) for t in ts)
            assert len(ts) == len(cls.__types__)

            # Resolve types!
            gen_map = {T: t for T, t in izip(cls.__types__, ts) if is_generic(T)}
            
            new_t = TraitImplT(gen_name(cls, ts), (cls,TraitImpl), {
                '__typemap__': gen_map
            })

            TRAIT_ABS_CACHE[(cls, ts)] = new_t

        return TRAIT_ABS_CACHE[(cls, ts)]


def get_attr(attrs, bases, attrName):
    """bfs"""
    s = list(bases)
    seen = set(s)
    it = iter(s)
    while True:
        if attrName in attrs:
            return attrs[attrName]

        next_base = next(it, None)
        if next_base is None:
            return None

        s.extend(b for b in next_base.__bases__ if b not in seen)
        seen.update(next_base.__bases__)
        attrs = next_base.__dict__

TRAIT_IMPL_CACHE = {}

class TraitImplT(TraitAbsT):
    """
    If a typemap is fufilled, need to confirm that the generic interfaces
    are also implemented.
    """
    
    def __new__(cls, name, bases, attrs):
        # Resolve each function with their types
        new_attrs = {}
        ts = get_attr(attrs, bases, '__typemap__') or {}
        if __debug__:
            iface = get_attr(attrs, bases, '__interface__') or {}

        for k, v in attrs.iteritems():
            if isinstance(v, Function):
                r_gens = [ts.get(t, t) for t in v.generics]
                v = v[tuple(r_gens)]
                if __debug__ and k in iface:
                    vi = iface[k]
                    r_gens = [ts.get(t, t) for t in vi.generics]
                    assert v.tEquals(vi[tuple(r_gens)])
            elif __debug__ and k in iface:
                raise AssertionError("Cannot change type from %s to %s" % (
                    iface[k], v))

            new_attrs[k] = v

        return type.__new__(cls, name, bases, new_attrs)

class Trait(object):
    __metaclass__ = TraitT

class TraitAbs(object):
    __metaclass__ = TraitAbsT

class TraitImpl(object):
    __metaclass__ = TraitAbsT
