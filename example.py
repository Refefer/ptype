from generics import A
from traits import Trait
from function import F0, Func
from typeclass import Typeclass, Implicit, Ev

@Typeclass
class Monoid(Trait[A]):

    @Func(object, A)
    def zero(object):
        raise NotImplementedError()

    @Func(object, A, A, A)
    def append(self, a, b):
        raise NotImplementedError()

@Implicit
class IntMonoid(Monoid[int]):

    @Func(object, int)
    def zero(self):
        return 0

    @Func(object, int, int, int)
    def append(self, a, b):
        return a + b


@Implicit
class StringMonoid(Monoid[str]):

    @Func(object, str)
    def zero(self):
        return ""

    @Func(object, str, str, str)
    def append(self, a, b):
        return a + b

@Func(list, A, Ev[Monoid[A]], A)
def join(lst, delim, ma):
    if len(lst) < 2:
        return lst

    it = iter(lst)
    agg = it.next()
    for item in it:
        agg = ma.append(ma.append(agg, delim), item)

    return agg

@Func(Ev[Monoid[A]], A)
def zero(ma):
    return ma.zero()
