from functools import partial
from itertools import izip

from generics import GenericType, is_generic, ImpT

def split_implicits(types):
    cTypes = []
    imps = []
    for t in types:
        (cTypes if isinstance(t, type) else imps).append(t)

    return cTypes, imps

def resolve_generics(types, ret):
    generics = set() 
    for ts in (types, (ret,)):
        for t in ts:
            if not is_generic(t): continue

            if isinstance(t, ImpT):
                generics.update(t.get_generics())
            else:
                generics.add(t)

    return list(generics)

class Function(object):

    def __init__(self, types, ret, f, allow_splats=False):
        assert isinstance(types, tuple)
        assert all(isinstance(t, (ImpT, type)) for t in types)
        assert isinstance(ret, type)
        if not allow_splats:
            assert f.func_code.co_argcount == len(types)

        # Total types
        self.types = types 

        # Concrete, passed in types
        self.cTypes, self.implicits = split_implicits(types)

        self.generics = resolve_generics(types, ret)

        self.polymorphic = len(self.generics) > 0
        self.cardinality = len(types)
        self.ret = ret
        self.f = f

    def _resolveArgs(self, args):
        new_args = []
        it = iter(args)
        for t in self.types:
            new_args.append(t.get() if isinstance(t, ImpT) else next(it))

        return tuple(new_args)

    def __call__(self, *args):

        if __debug__:
            assert len(args) == self.cardinality - len(self.implicits)

        # Generic?  Gotta build a fully formed function
        if self.polymorphic:
            return self._callGeneric(args)
        
        if __debug__:
            for p, t in izip(args, self.types):
                assert isinstance(p, t), \
                    "%s: Expected %s, got %s" % (
                        self.f.__name__, t.__name__, type(p).__name__
                    )

        r_args = self._resolveArgs(args)
        ret = self.f(*r_args)
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
        gs = [type(t) for T, t in izip(self.cTypes, args) 
                if is_generic(T)]
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
        new_types = []
        for t in self.types:
            new_t = t.resolve(gen_map) \
                if isinstance(t, ImpT) else gen_map.get(t, t)
            new_types.append(new_t)
        
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

    def tEquals(self, f):
        if not isinstance(f, Function): return False
        if self.cardinality != f.cardinality: return False
        if not all(t1==t2 for t1, t2 in izip(self.types, f.types)): return False
        if len(self.generics) != len(f.generics): return False
        if len(set(self.generics) ^ set(f.generics)) > 0: return False
        if self.ret != f.ret: return False
        return True



def F0(ret):
    return partial(Function, (), ret)

def FUnit(*types):
    return partial(Function, types, NoneType)

def Func(*types):
    assert len(types) > 0
    return partial(Function, tuple(types[:-1]), types[-1])

def is_polymorphic(v, on_types=None):
    """
    Tests if a function is polymorphic.  If `on_types` is provided, checks
    to see if a function is generic on the set of provided types.
    """
    if isinstance(v, Function) and v.polymorphic:
        if on_types is not None:
            gens = set(on_types)
            return len(gens.intersection(v.generics)) > 0
        else:
            return True
    return False
