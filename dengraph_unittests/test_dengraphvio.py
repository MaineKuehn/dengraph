import textwrap

import dengraph.graphs.graph_io
import dengraph.distance

from dengraph_unittests.utility import unittest

from dengraph.distances.delta_distance import DeltaDistance, IncrementalDeltaDistance
from dengraph.graphs.distance_graph import DistanceGraph
from dengraph.dengraphvio import DenGraphVIO


class IncrementalListDistance(dengraph.distance.Distance):
    def __call__(self, x, y, default=None):
        if isinstance(y, list):
            y = y[0]
        return abs(x - y)

    def mean(self, *args, **kwargs):
        if len(args) == 1:
            args = args[0]
        try:
            return sum(args) / float(len(args))
        except ZeroDivisionError:
            if "default" in kwargs:
                return kwargs.get("default")
            raise ValueError()

    def update(self, static, dynamic, dynamic_changes, base_distance=0, default=None):
        result = base_distance
        for change in dynamic_changes:
            result = self(base_distance, change)
        return result


class TestDenGraphVIO(unittest.TestCase):
    def test_creation(self):
        io_graph = DenGraphVIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4, 5, 6], distance=DeltaDistance(), symmetric=True
            ),
            cluster_distance=5,
            core_neighbours=5,
        )
        self.assertIsNotNone(io_graph)

        literal = textwrap.dedent(
            """
        1,2,3,4,5,6
        0,1,1,1,1,1
        1,0,1,1,1,1
        1,1,0,1,1,1
        1,1,1,0,1,1
        1,1,1,1,0,1
        1,1,1,1,1,0
        """.strip()
        )
        with self.assertRaises(dengraph.distance.NoDistanceSupport):
            io_graph = DenGraphVIO(
                base_graph=dengraph.graphs.graph_io.csv_graph_reader(
                    literal.splitlines(), symmetric=True
                ),
                cluster_distance=5,
                core_neighbours=5,
            )

    def test_simple(self):
        io_graph = DenGraphVIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4, 5, 6], distance=DeltaDistance(), symmetric=True
            ),
            cluster_distance=5,
            core_neighbours=5,
        )
        cluster, distance = next(io_graph.probe(1))
        self.assertEqual(2.5, distance)
        io_graph[7] = {}
        cluster, distance = next(io_graph.probe(1))
        # expecting that algorithm uses cached mean
        self.assertEqual(2.5, distance)

    def test_simple_incremental(self):
        io_graph = DenGraphVIO(
            base_graph=DistanceGraph(
                nodes=[1, 2, 3, 4, 5, 6],
                distance=IncrementalListDistance(),
                symmetric=True,
            ),
            cluster_distance=5,
            core_neighbours=5,
        )
        base_object = [1]
        io_graph.probe(base_object)
        for i in range(1, 4):
            cluster, current_distance = next(io_graph.probe([1 + i]))
            _, new_distance = next(io_graph.update_probe(base_object, [1]))
            base_object[0] += 1
            self.assertEqual(current_distance, new_distance)
