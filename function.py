from functools import partial
from itertools import izip

from generics import GenericType, is_generic

class Function(object):

    def __init__(self, types, ret, f, allow_splats=False):
        assert isinstance(types, tuple)
        assert all(isinstance(t, type) for t in types)
        assert isinstance(ret, type)
        if not allow_splats:
            assert f.func_code.co_argcount == len(types)

        self.types = types 
        self.generics = list({t for ts in (types, (ret,)) 
            for t in ts if is_generic(t)})

        self.polymorphic = len(self.generics) > 0
        self.cardinality = len(types)
        self.ret = ret
        self.f = f

    def __call__(self, *args):

        if __debug__:
            assert len(args) == self.cardinality

        # Generic?  Gotta build a fully formed function
        if self.polymorphic:
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

    def __get__(self, inst, cls):
        if inst is None: return self

        _self = self
        f = partial(self, inst)
        f.__name__ = self.f.__name__
        return Function(tuple(self.types[1:]), self.ret, f, allow_splats=True)

    def _callGeneric(self, args):
        gs = [type(t) for T, t in izip(self.types, args) if is_generic(T)]
        new_f = self[tuple(gs)]
        # Return type _must_ be known at call time
        assert not is_generic(new_f.ret)
        return new_f(*args)

    def __getitem__(self, ts):
        """
        Take generics, make them less generic!
        """
        ts = ts if isinstance(ts, tuple) else (ts,)
        assert len(self.generics) == len(ts)

        gen_map = {g: t for g, t in izip(self.generics, ts)}
        new_types = [gen_map.get(t, t) for t in self.types]
        
        # Resolve return type, if we can
        ret = gen_map[self.ret] if is_generic(self.ret) else self.ret

        return Function(tuple(new_types), ret, self.f)

    def andThen(self, func):
        assert isinstance(func, Function)
        assert func.cardinality == 1
        assert issubclass(self.ret, func.types[0])
        
        def _f(*args, **kwargs):
            return func(*self(*args, **kwargs))

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
        if self.polymorphic:
            gtypes = '[%s]' % ", ".join(t.__name__ for t in self.generics)
        else:
            gtypes = ''

        return "%s%s(%s): %s" % (self.f.__name__, 
                gtypes,
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

