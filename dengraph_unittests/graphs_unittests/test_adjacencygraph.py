import unittest
import random
import itertools
import textwrap



import dengraph.graph
import dengraph.graphs.graph_io
import dengraph.graphs.adjacency_graph
from dengraph.graph import NoSuchNode


class TestAdjacencyGraph(unittest.TestCase):
    @staticmethod
    def random_content(length, connections=None, distance_range=1.0):
        connections, have_connections = connections if connections is not None else length * length / 2, 0
        # create nodes
        adjacency = {random.randint(0, length * 10) : {} for _ in range(length)}
        while len(adjacency) < length:  # postfix collisions
            adjacency[random.randint(0, length * 10)] = {}
        # connect nodes randomly
        nodes = list(adjacency)
        while have_connections < connections:
            for node in nodes:
                neighbour = random.choice(nodes)
                if neighbour not in adjacency[node]:
                    adjacency[node][neighbour] = random.random() * distance_range
                    adjacency[neighbour][node] = adjacency[node][neighbour]
                    have_connections += 1
        return adjacency

    def make_content_samples(self, lengths=range(5, 101, 20), connections=None, distance_range=1.0):
        yield {
            1: {2: 0.25},
            2: {1: 0.25, 3: 0.5},
            3: {2: 0.5, 4: 0.35},
            4: {3: 0.35}
        }  # fixed example
        connections = connections if connections is not None else [None] * len(lengths)
        for idx, length in enumerate(lengths):
            yield self.random_content(length, connections[idx], distance_range)

    def test_construct_dict(self):
        pass

    def test_creation(self):
        literal = textwrap.dedent("""
        1,2,3,4,5,6,7,8
        0,1,1,1,1,2,0,1
        1,0,0,0,0,0,0,0
        1,0,0,0,0,0,0,0
        1,0,0,0,0,0,0,0
        1,0,0,0,0,0,0,0
        2,0,0,0,0,0,1,0
        0,0,0,0,0,1,0,0
        1,0,0,0,0,0,0,0
        """.strip())
        graph = dengraph.graphs.graph_io.csv_graph_reader(literal.splitlines(), symmetric=True)
        self.assertTrue(slice("6", "1") in graph)
        al_graph = dengraph.graphs.adjacency_graph.AdjacencyGraph(source=graph, max_distance=1)
        self.assertEqual(1, al_graph["6":"7"])
        self.assertEqual(1, al_graph["7":"6"])
        with self.assertRaises(dengraph.graph.NoSuchEdge):
            al_graph["1":"6"]
        with self.assertRaises(dengraph.graph.NoSuchEdge):
            al_graph["6":"1"]
        # create empty graph
        al_graph = dengraph.graphs.adjacency_graph.AdjacencyGraph(max_distance=1)
        self.assertIsNotNone(al_graph)
        # create graph from wrong type
        with self.assertRaises(TypeError):
            dengraph.graphs.adjacency_graph.AdjacencyGraph(source=[1, 2, 3])

    def test_containment(self):
        graph = dengraph.graphs.adjacency_graph.AdjacencyGraph(source={
            1: {2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 8: 1},
            2: {1: 1},
            3: {1: 1},
            4: {1: 1},
            5: {1: 1},
            6: {1: 2, 7: 1},
            7: {6: 1},
            8: {1: 1}
        }, max_distance=1)
        self.assertTrue(1 in graph)
        self.assertTrue(6 in graph)
        self.assertTrue(slice(6, 7) in graph)
        self.assertFalse(slice(1, 6) in graph)
        self.assertFalse(slice(6, 1) in graph)

    def test_get(self):
        graph = dengraph.graphs.adjacency_graph.AdjacencyGraph(source={
            1: {2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 8: 1},
            2: {1: 1},
            3: {1: 1},
            4: {1: 1},
            5: {1: 1},
            6: {1: 2, 7: 1},
            7: {6: 1},
            8: {1: 1}
        }, max_distance=2)
        self.assertEqual(1, graph[1:2])
        self.assertEqual(2, graph[6:1])
        with self.assertRaises(dengraph.graph.NoSuchEdge):
            graph[8:7]
        with self.assertRaises(dengraph.graph.NoSuchEdge):
            graph[9:10]
        with self.assertRaises(TypeError):
            graph[8]

    def test_set(self):
        graph = dengraph.graphs.adjacency_graph.AdjacencyGraph(source={
            1: {2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 8: 1},
            2: {1: 1},
            3: {1: 1},
            4: {1: 1},
            5: {1: 1},
            6: {1: 2, 7: 1},
            7: {6: 1},
            8: {1: 1}
        }, max_distance=1)
        self.assertFalse(slice(1, 6) in graph)
        graph[1:6] = 2
        self.assertEqual(2, graph[1:6])
        with self.assertRaises(dengraph.graph.NoSuchNode):
            graph[1:9] = 1
        with self.assertRaises(dengraph.graph.NoSuchNode):
            graph[9:1] = 1
        graph[9] = {}
        graph[9:1] = 1
        self.assertEqual(1, graph[1:9])
