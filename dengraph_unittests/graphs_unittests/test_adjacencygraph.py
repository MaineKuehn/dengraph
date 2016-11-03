import unittest
import random
import itertools


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