import textwrap
import unittest


import dengraph.graph
import dengraph.graphs.graph_io


class GraphIOTest(unittest.TestCase):
    def test_default(self):
        """
        Test evaluation using default settings

        string header, literals, any distance, ignore bool-False edges, asymmetric
        """
        literal = textwrap.dedent("""
        a,b,c,d
        0, 1,2,5
        1, 0,1,2
        2, 1,0,1
        5.2,16,None,5
        """.strip())
        graph = dengraph.graphs.graph_io.csv_graph_reader(literal.splitlines())
        # a row
        self.assertEqual(graph['a':'b'], 1)
        self.assertEqual(graph['a':'c'], 2)
        self.assertEqual(graph['a':'d'], 5)
        # b row
        self.assertEqual(graph['b':'a'], 1)
        self.assertEqual(graph['b':'c'], 1)
        self.assertEqual(graph['b':'d'], 2)
        # c row
        self.assertEqual(graph['c':'a'], 2)
        self.assertEqual(graph['c':'b'], 1)
        self.assertEqual(graph['c':'d'], 1)
        # d row
        self.assertEqual(graph['d':'a'], 5.2)
        self.assertEqual(graph['d':'b'], 16)
        self.assertEqual(graph['d':'d'], 5)
        # removed edges
        with self.assertRaises(dengraph.graph.NoSuchEdge):
            graph['a':'a']
        with self.assertRaises(dengraph.graph.NoSuchEdge):
            graph['b':'b']
        with self.assertRaises(dengraph.graph.NoSuchEdge):
            graph['c':'c']
        with self.assertRaises(dengraph.graph.NoSuchEdge):
            graph['d':'c']

