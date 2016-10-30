import textwrap
import unittest


import dengraph.graph
import dengraph.graphs.graph_io


class GraphIOTest(unittest.TestCase):
    @staticmethod
    def generate_matrix_csv(size=4, separator=','):
        literal = '\n'.join(
            separator.join(str(rval - cval) for cval in range(size))
            for rval in range(size)
        )
        return literal

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

    def test_header_none(self):
        """Test default, enumerated header"""
        for size in (1, 5, 10, 20):
            literal = self.generate_matrix_csv(size)
            graph = dengraph.graphs.graph_io.csv_graph_reader(literal.splitlines(), nodes_header=False)
            self.assertHeaderMatrixGraph(list(range(size)), graph)

    def test_header_iterable(self):
        """Test header from iterable"""
        for size in (1, 5, 10, 20):
            header = ['N%02d' % num for num in range(size)]
            literal = self.generate_matrix_csv(size)
            graph = dengraph.graphs.graph_io.csv_graph_reader(literal.splitlines(), nodes_header=header)
            self.assertHeaderMatrixGraph(header, graph)

    def test_header_strings(self):
        """Test header from first line as strings"""
        for size in (1, 5, 10, 20):
            header = ['N%02d' % num for num in range(size)]
            literal = ','.join(header) + '\n' + self.generate_matrix_csv(size)
            graph = dengraph.graphs.graph_io.csv_graph_reader(literal.splitlines(), nodes_header=True)
            self.assertHeaderMatrixGraph(header, graph)

    def test_header_call(self):
        """Test header from first line as strings"""
        for size in (1, 5, 10, 20):
            header = ['%2d' % num for num in range(size)]
            literal = ','.join(header) + '\n' + self.generate_matrix_csv(size)
            graph = dengraph.graphs.graph_io.csv_graph_reader(literal.splitlines(), nodes_header=lambda elem: int(elem))
            self.assertHeaderMatrixGraph(list(range(size)), graph)

    def assertHeaderMatrixGraph(self, header, graph):
            self.assertEqual(sorted(graph), sorted(header))
            for row_idx, node_from in enumerate(header):
                for column_idx, node_to in enumerate(header):
                    if column_idx == row_idx:
                        with self.assertRaises(dengraph.graph.NoSuchEdge):
                            graph[node_from:node_to]
                    else:
                        self.assertEqual(graph[node_from:node_to], row_idx - column_idx)
