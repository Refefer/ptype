from functools import partial
from itertools import izip

from generics import GenericType

class Function(object):

    def __init__(self, types, ret, f):
        assert all(isinstance(t, type) for t in types)
        assert isinstance(ret, type)
        assert f.func_code.co_argcount == len(types)
        self.types = types 
        self.generic = any(issubclass(t, GenericType) for t in types)
        self.cardinality = len(types)
        self.ret = ret
        self.f = f

    def __call__(self, *args):
        if __debug__:
            assert len(args) == self.cardinality

        # Generic?  Gotta build a fully formed function
        if self.generic:
            return self._callGeneric(args)
        
        if __debug__:
            for p, t in izip(args, self.types):
                assert isinstance(p, t), \
                    "%s: Expected %s, got %s" % (
                        self.f.__name__, t.__name__, type(p).__name__
                    )

        ret = self.f(*args)
        if __debug__:
            assert isinstance(ret, self.ret), \
                "%s: Expected %s, got %s" % (
                        self.f.__name__, self.ret.__name__, type(ret).__name__
                )
                                             

        return ret

    def _callGeneric(self, args):
        gens = {}
        types = []
        for t, v in izip(self.types, args):
            if issubclass(t, GenericType):
                if t not in gens:
                    gens[t] = type(v)

                types.append(gens[t])

        # Resolve ret
        ret = gens[self.ret] if issubclass(self.ret, GenericType) else self.ret
            
        return Function(types, ret, self.f)(*args)

    def andThen(self, func):
        assert isinstance(func, Function)
        assert func.cardinality == 1
        assert issubclass(self.ret, func.types[0])
        
        this = self
        def _f(*args, **kwargs):
            return func(*this(*args, **kwargs))

        return Function(self.types, func.ret, _f)

    def compose(self, func):
        return func.andThen(self)

    def _curry(self, leftVs, rightTs, ret, f):
        if len(rightTs) == 0:
            return f(*leftVs)

        newRet = ret if len(rightTs) == 1 else Function
        @Func(rightTs[0], newRet)
        def _f(rightT):
            return self._curry(leftVs + (rightT,), rightTs[1:], ret, f)

        return _f

    @property
    def curry(self):
        if self.cardinality > 1:
            return self._curry((), self.types, self.ret, self.f)

        return self

    def __str__(self):
        return "%s(%s): %s" % (self.f.__name__, 
                ", ".join(t.__name__ for t in self.types),
                self.ret.__name__)

    __repr__ = __str__

def F0(ret):
    return partial(Function, (), ret)

def FUnit(*types):
    return partial(Function, types, NoneType)

def Func(*types):
    assert len(types) > 0
    return partial(Function, tuple(types[:-1]), types[-1])
