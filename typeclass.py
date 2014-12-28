from generics import ImpT, is_generic

_T_CLASS = {}
def Typeclass(cls):
    from traits import get_attr, Trait
    for t in cls.__bases__:
        if issubclass(t, Trait):
            assert t not in _T_CLASS, "Typeclass already specified!"
            assert len(get_attr({}, (t,), '__types__')) == 1, \
                    "Typeclasses must be of shape 1"

            _T_CLASS[cls] = {}

    return cls

def Implicit(cls):
    has_implicit = False
    for t in cls.__bases__:
        for st in t.__bases__:
            if st in _T_CLASS:
                assert t not in _T_CLASS[st], \
                        "Implicit %s is already defined" % t
                inst = cls()
                _T_CLASS[st][t] = lambda: inst
                has_implicit = True

    assert has_implicit, "No typeclass found for %s" % cls

    return cls

class _implicitly(object):
    def __init__(self, lookup):
        self.lookup = lookup

    def __getitem__(self, tc_inst):
        tc = tc_inst.__bases__[0]
        assert tc in self.lookup and tc_inst in self.lookup[tc], \
                "No Typeclass implementation found for %s" % tc_inst
        return self.lookup[tc][tc_inst]()

implicitly = _implicitly(_T_CLASS)

class TCGenResolver(ImpT):
    def __init__(self, base, type_var, name):
        self.base = base
        self.type_var = type_var
        self.name = name

    def get_generics(self):
        return (self.type_var,)

    def resolve(self, type_map):
        t = self.base[type_map[self.type_var]]
        return TCImpResolver(implicitly[t], t.__name__)

    def get(self):
        raise AssertionError("Should not be able to get!")

    @property
    def __name__(self):
        return self.name

class TCImpResolver(ImpT):
    def __init__(self, item, name):
        self.item = item
        self.name = name

    def get_generics(self):
        return ()

    def resolve(self, _type_map):
        return self

    def get(self):
        return self.item

    @property
    def __name__(self):
        return self.name

class EvT(type):
    def __getitem__(self, tc):
        base = tc.__bases__[0]
        type_var = tc.__types__[0]
        assert base in _T_CLASS
        assert is_generic(type_var)
        return TCGenResolver(base, type_var, tc.__name__)

class Ev(object):
    __metaclass__ = EvT
