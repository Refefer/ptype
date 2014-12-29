import unittest
from generics import A, B
from function import F0, Func, FUnit
from traits import Trait

class TraitTest(unittest.TestCase):

    def test_Trait_monomorph(self):
        class Foo(Trait):

            @Func(object, int)
            def bar(self):
                return 1

        foo = Foo()
        self.assertEquals(foo.bar(), 1)

    def _build_monoid(self):
        class Monoid(Trait[A]):

            @Func(object, A)
            def zero(self):
                raise NotImplementedError()

            @Func(object, A, A, A)
            def append(self, a, b):
                raise NotImplementedError()

        return Monoid

    def test_polymorphic_b1(self):
        """
        Tests that an error is thrown when extending incorrectly
        """
        monoid = self._build_monoid()
        def _build_bad_impl():
            class BadMonoid(monoid[int]):

                @Func(object, int)
                def zero(self):
                    return 0

                @Func(object, int, int, str)
                def append(self, a, b):
                    return "yo"

        self.failUnlessRaises(AssertionError, _build_bad_impl)

    def _build_int_monoid(self):
        class IntMonoid(self._build_monoid()[int]):
            @Func(object, int)
            def zero(self):
                return 0

            @Func(object, int, int, int)
            def append(self, a, b):
                return a + b
        return IntMonoid

    def test_polymorphic_good(self):
                    
        im = self._build_int_monoid()()
        self.assertEquals(im.zero(), 0)
        self.assertEquals(im.append(1, 2), 3)

    def test_polymorphic_good_2(self):
        class ProductIntMonoid(self._build_int_monoid()):
            @Func(object, int)
            def zero(self): return 1

            @Func(object, int, int, int)
            def append(self, a, b): return a * b

        pim = ProductIntMonoid()
        self.assertEquals(pim.zero(), 1)
        self.assertEquals(pim.append(2,3), 6)

    def test_polymorphic_bad_2(self):
        def bad():
            class BadIntMonoid(self._build_int_monoid()):
                @Func(object, str)
                def zero(self): return "1"

        self.failUnlessRaises(AssertionError, bad)

if __name__ == '__main__':
    unittest.main()
