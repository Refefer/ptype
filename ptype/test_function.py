import unittest
from generics import A, B
from function import F0, Func, FUnit

class FunctionTest(unittest.TestCase):

    def test_F0_concrete(self):
        """
        Makes sure it works as we'd expect for concrete types
        """
        @F0(int)
        def zero():
            return 1

        self.assertEquals(zero(), 1)

    def test_F0_generic(self):

        @F0(A)
        def foo():
            return 1

        self.failUnlessRaises(AssertionError, foo)
        
        self.assertEquals(foo[int](), 1)

if __name__ == '__main__':
    unittest.main()
