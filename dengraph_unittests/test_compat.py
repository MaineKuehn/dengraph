try:
    import unittest2 as unittest
except ImportError:
    import unittest

from dengraph import compat


class TestCompat(unittest.TestCase):
    """Tests for python version compatibility helpers"""
    def test_abc(self):
        """ABC Baseclass"""
        class ABC(compat.ABCBase):
            pass

        @ABC.register
        class ABCImplementation(object):
            pass
        self.assertIsInstance(ABCImplementation(), ABC)

    def test_range(self):
        """Py3.X range"""
        self.assertNotIsInstance(compat.range(5), list)
        self.assertEqual(list(compat.range(10)), range(10))
        self.assertIn(19, compat.range(15, 20))
        self.assertNotIn(25, compat.range(25))

    def test_views(self):
        """Dict views"""
        t_dict = {1: 1.0, 'b': 'B', False: True, 'dict': {}}
        self.assertNotIsInstance(compat.viewitems(t_dict), list)
        self.assertNotIsInstance(compat.viewkeys(t_dict), list)
        self.assertNotIsInstance(compat.viewvalues(t_dict), list)
        self.assertEqual(list(compat.viewkeys(t_dict)), list(t_dict.keys()))
        self.assertEqual(list(compat.viewvalues(t_dict)), list(t_dict.values()))
        self.assertEqual(list(compat.viewitems(t_dict)), list(t_dict.items()))
