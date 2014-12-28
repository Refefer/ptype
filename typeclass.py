from traits import get_attr, Trait

_T_CLASS = {}
def Typeclass(cls):
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
