import unittest

from dengraph.cluster import DenGraphCluster, GraphError
from dengraph.graphs.distance_graph import DistanceGraph


class TestDenGraphCluster(unittest.TestCase):
    def test_creation(self):
        cluster = DenGraphCluster(graph=DistanceGraph(
            nodes=[1, 2, 3],
            distance=None,
            symmetric=True
        ))
        self.assertEqual(cluster.core_nodes, set())
        self.assertEqual(cluster.border_nodes, set())
        cluster.categorize_node(1, cluster.BORDER_NODE)
        cluster.categorize_node(1, cluster.CORE_NODE)
        self.assertTrue(1 in cluster.core_nodes and 1 not in cluster.border_nodes)
        cluster.categorize_node(1, cluster.BORDER_NODE)
        self.assertTrue(1 in cluster.border_nodes and 1 not in cluster.core_nodes)

    def test_add_differing_graphs(self):
        cluster_a = DenGraphCluster(graph=DistanceGraph(
            nodes=[1, 2, 3],
            distance=None,
            symmetric=True
        ))
        cluster_b = DenGraphCluster(graph=DistanceGraph(
            nodes=[2, 3, 4],
            distance=None,
            symmetric=True
        ))
        with self.assertRaises(GraphError):
            cluster_a + cluster_b

    def test_add(self):
        graph = DistanceGraph(
            nodes=[1, 2, 3, 4],
            distance=None,
            symmetric=True
        )
        cluster_a = DenGraphCluster(graph=graph)
        cluster_b = DenGraphCluster(graph=graph)
        cluster_a.border_nodes = set([2,3])
        cluster_a.core_nodes = set([1])
        cluster_b.border_nodes = set([3,4])
        cluster_b.core_nodes = set([2])

        cluster_c = cluster_a + cluster_b
        self.assertNotEqual(cluster_c, cluster_a)
        self.assertNotEqual(cluster_c, cluster_b)
        self.assertEqual(set([1, 2]), cluster_c.core_nodes)
        self.assertEqual(set([3, 4]), cluster_c.border_nodes)

    def test_inplace_add(self):
        graph = DistanceGraph(
            nodes=[1, 2, 3, 4],
            distance=None,
            symmetric=True
        )
        cluster_a = DenGraphCluster(graph)
        cluster_b = DenGraphCluster(graph)
        cluster_a.border_nodes = set([2,3])
        cluster_a.core_nodes = set([1])
        cluster_b.border_nodes = set([3,4])
        cluster_b.core_nodes = set([2])

        cluster_a += cluster_b
        self.assertEqual(set([1, 2]), cluster_a.core_nodes)
        self.assertEqual(set([3, 4]), cluster_a.border_nodes)
