from collections import Iterable

from ptype.generics import A, B
from ptype.traits import Trait
from ptype.function import F0, Func
from ptype.typeclass import Typeclass, Implicit, Ev

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

@Implicit
class ListMonoid(Monoid[list]):

    @Func(object, list)
    def zero(self):
        return []

    @Func(object, list, list, list)
    def append(self, a, b):
        return a + b

@Implicit
class IteratorMonoid(Monoid[Iterable]):
    @Func(object, Iterable)
    def zero(self):
        return iter(())

    @Func(object, Iterable, Iterable, Iterable)
    def append(self, a, b):
        for it in (a,b):
            for i in it:
                yield i

@Func(list, A, Ev[Monoid[A]], A)
def join(lst, delim, ma):
    if len(lst) == 0:
        return ma.zero()

    it = iter(lst)
    agg = it.next()
    for item in it:
        agg = ma.append(ma.append(agg, delim), item)

    return agg

@Func(Ev[Monoid[A]], A)
def zero(ma):
    return ma.zero()

@Func(Ev[Monoid[A]], Ev[Monoid[B]], tuple)
def zTup(ma, mb):
    return (ma.zero(), mb.zero())
