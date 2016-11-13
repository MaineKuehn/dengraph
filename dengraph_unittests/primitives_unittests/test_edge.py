try:
    import unittest2 as unittest
except ImportError:
    import unittest

from dengraph.primitives import edge


class TestEdge(unittest.TestCase):
    def test_call(self):
        self.assertIsInstance(edge.Edge(1, 2), slice)
        with self.assertRaises(TypeError):
            edge.Edge(1)

    def test_getitem(self):
        self.assertIsInstance(edge.Edge[1:2], slice)
        with self.assertRaises(TypeError):
            edge.Edge[1]
        with self.assertRaises(TypeError):
            edge.Edge[1, 2]
