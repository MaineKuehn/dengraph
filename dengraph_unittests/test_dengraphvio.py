import textwrap

import dengraph.graphs.graph_io
import dengraph.distance

from dengraph_unittests.utility import unittest

from dengraph.distances.delta_distance import DeltaDistance, IncrementalDeltaDistance
from dengraph.graphs.distance_graph import DistanceGraph
from dengraph.dengraphvio import DenGraphVIO


class TestDenGraphVIO(unittest.TestCase):
    def test_creation(self):
        io_graph = DenGraphVIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4, 5, 6],
                distance=DeltaDistance(),
                symmetric=True
            ),
            cluster_distance=5,
            core_neighbours=5
        )
        self.assertIsNotNone(io_graph)

        literal = textwrap.dedent("""
        1,2,3,4,5,6
        0,1,1,1,1,1
        1,0,1,1,1,1
        1,1,0,1,1,1
        1,1,1,0,1,1
        1,1,1,1,0,1
        1,1,1,1,1,0
        """.strip())
        with self.assertRaises(dengraph.distance.NoDistanceSupport):
            io_graph = DenGraphVIO(
                base_graph=dengraph.graphs.graph_io.csv_graph_reader(literal.splitlines(), symmetric=True),
                cluster_distance=5,
                core_neighbours=5
            )

    def test_simple(self):
        io_graph = DenGraphVIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4, 5, 6],
                distance=DeltaDistance(),
                symmetric=True
            ),
            cluster_distance=5,
            core_neighbours=5
        )
        _, distance = next(io_graph.probe(1))
        self.assertEqual(2.5, distance)
        io_graph[7] = {}
        _, distance = next(io_graph.probe(1))
        self.assertEqual(3.0, distance)

    def test_simple_incremental(self):
        io_graph = DenGraphVIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4, 5, 6],
                distance=IncrementalDeltaDistance(),
                symmetric=True
            ),
            cluster_distance=5,
            core_neighbours=5
        )
        cluster, base_distance = next(io_graph.probe(1))
        for i in range(1, 4):
            cluster, current_distance = next(io_graph.probe(1+i))
            self.assertEqual(current_distance, io_graph.update_probe(1, base_distance, cluster))
            base_distance = current_distance
