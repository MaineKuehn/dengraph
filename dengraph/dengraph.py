# -*- coding: utf-8 -*-
from __future__ import absolute_import
import dengraph.graph
import dengraph.cluster
import dengraph.utilities.pretty


class NoSuchCluster(Exception):
    pass


class DenGraphIO(dengraph.graph.Graph):
    """
    Density Graph Clustering allowing for Overlap and Incremental updates.

    :param base_graph: the underlying graph
    :param cluster_distance: maximum distance for nodes to be considered as neighbours (ε)
    :param core_neighbours: number of neighbours required for core nodes (η)
    """

    def __init__(self, base_graph, cluster_distance, core_neighbours):
        """
        :param base_graph: the underlying graph
        :param cluster_distance: eta
        :param core_neighbours: epsilon
        """
        self.graph = base_graph
        self.cluster_distance = cluster_distance
        self.core_neighbours = core_neighbours
        self.clusters = []
        self.noise = set()
        self._init_cluster()

    def _merge_clusters(self, base_cluster, cluster):
        base_cluster += cluster
        if base_cluster != cluster:
            try:
                self.clusters.remove(cluster)
            except ValueError:
                pass
        return base_cluster

    def core_cluster_for_node(self, core_node):
        """
        Method determines the current clusters a node belongs to and is labeled as core node.

        :param core_node: the core node to check cluster for
        :return: Cluster that nas node as a core node
        :raise: NoSuchCluster
        """
        for cluster in self.clusters:
            if core_node in cluster.core_nodes:
                return cluster
        raise NoSuchCluster

    def clusters_for_node(self, node):
        """
        Method yields all clusters the given node is part of.

        :param node: the node to check clusters for
        :return: Cluster generator
        """
        for cluster in self.clusters:
            if node in cluster:
                yield cluster

    def _add_node_to_cluster(self, node, cluster, state):
        """Mark a node as belonging to a specific cluster"""
        cluster.categorize_node(node, state)
        self.noise.discard(node)

    def _test_change_to_core(self, node):
        """
        Method determines if a given node does become a core node. This method returns False,
        if the node is already a core node.

        :param node: The node to check
        :return: True, if node changes to core node, False otherwise
        """
        result = False
        # determine the neighbours of current node
        neighbours = set(self.graph.get_neighbours(node, self.cluster_distance))
        try:
            cluster = self.core_cluster_for_node(core_node=node)
        except NoSuchCluster:
            result = len(neighbours) >= self.core_neighbours
            cluster = None
        # return the current result and also the neighbours for further reference
        return result, cluster, neighbours

    def _test_change_from_core(self, node):
        result = False
        neighbours = set(self.graph.get_neighbours(node, self.cluster_distance))
        try:
            cluster = self.core_cluster_for_node(core_node=node)
        except NoSuchCluster:
            # node was no core before, so False is returned
            cluster = None
        else:
            result = len(neighbours) < self.core_neighbours
        return result, cluster, neighbours

    # TODO: to be changed
    def _recluster(self, cluster):
        clustering = DenGraphIO(
            base_graph=cluster,
            cluster_distance=self.cluster_distance,
            core_neighbours=self.core_neighbours
        )
        self.noise.update(clustering.noise)
        self.clusters.remove(cluster)
        self.clusters.extend(clustering.clusters)

    def _cluster_removed(self, cluster):
        for node in cluster.border_nodes:
            clusters = self.clusters_for_node(node=node)
            try:
                # check whether there is at least one additional cluster containing node
                next(clusters)
                next(clusters)
            except StopIteration:
                self.noise.add(node)
        try:
            self.clusters.remove(cluster)
        except ValueError:
            pass

    def _cluster_added(self, cluster):
        for node in cluster:
            self.noise.discard(node)
        self.clusters.append(cluster)

    def _validate_cluster(self, cluster, nodes, base=None):
        unchecked, checked = set(nodes), set(nodes)
        tmp_cluster = dengraph.cluster.DenGraphCluster(graph=self.graph)
        while unchecked:
            checking = unchecked.pop()
            if checking == base:
                return
            neighbours = set(cluster.get_neighbours(node=checking,
                                                distance=self.cluster_distance))
            if len(neighbours) >= self.core_neighbours:
                tmp_cluster.categorize_node(checking, tmp_cluster.CORE_NODE)
                self._expand_unchecked(unchecked=unchecked, checked=checked, neighbours=neighbours)
            elif neighbours:
                tmp_cluster.categorize_node(checking, tmp_cluster.BORDER_NODE)
        return tmp_cluster

    def _remove_noise(self, candidates):
        for candidate in candidates:
            clusters = self.clusters_for_node(node=candidate)
            try:
                # noise is contained in no clusters
                next(clusters)
            except StopIteration:
                self.noise.add(candidate)

    def _edge_removed(self, node):
        is_downgraded, cluster, _ = self._test_change_from_core(node=node)
        if is_downgraded:
            self._add_node_to_cluster(node=node, cluster=cluster, state=cluster.BORDER_NODE)
            if not cluster.core_nodes:
                # remove cluster
                self._cluster_removed(cluster=cluster)

    def _check_cluster(self, nodes, core_cluster):
        missing = set(nodes)
        try:
            new_cluster = self._validate_cluster(cluster=core_cluster, nodes=[missing.pop()])
            missing -= new_cluster.core_nodes
            noise = core_cluster.core_nodes.union(core_cluster.border_nodes) - \
                new_cluster.core_nodes - new_cluster.border_nodes
            while missing:
                split_cluster = self._validate_cluster(cluster=core_cluster, nodes=[missing.pop()])
                if split_cluster.core_nodes:
                    self._cluster_added(split_cluster)
                    noise -= split_cluster.core_nodes.union(split_cluster.border_nodes)
                    missing -= split_cluster.core_nodes
            self._cluster_removed(cluster=core_cluster)
            if new_cluster.core_nodes:
                self._cluster_added(new_cluster)
            self._remove_noise(candidates=noise)
        except KeyError:
            if len(core_cluster.core_nodes) <= 1:
                self._cluster_removed(core_cluster)

    def _node_removed(self, node, neighbours):
        if node not in self.noise:
            for neighbour in neighbours:
                del self.graph[neighbour:node]
                del self.graph[node:neighbour]
                self._edge_removed(node=neighbour)
            cluster = self.core_cluster_for_node(core_node=node)
            self._check_cluster(
                nodes=[neighbour for neighbour in neighbours if neighbour in cluster.core_nodes],
                core_cluster=cluster)
        self.noise.discard(node)

    def _merge_neighbours(self, neighbours, cluster):
        for neighbour in neighbours:
            try:
                neighbouring_cluster = self.core_cluster_for_node(core_node=neighbour)
                cluster = self._merge_clusters(cluster, neighbouring_cluster)
            except NoSuchCluster:
                # node is no core
                self._add_node_to_cluster(node=neighbour, cluster=cluster, state=cluster.BORDER_NODE)
        return cluster

    def _edge_added(self, nodes, new_node=None):
        for node in nodes:
            becomes_core, cluster, neighbours = self._test_change_to_core(node=node)
            if becomes_core:
                this_cluster = dengraph.cluster.DenGraphCluster(self.graph)
                self.clusters.append(this_cluster)
                self._add_node_to_cluster(node=node, cluster=this_cluster, state=this_cluster.CORE_NODE)
                self._merge_neighbours(neighbours=neighbours, cluster=this_cluster)
            elif cluster and new_node:
                self._add_node_to_cluster(node=new_node, cluster=cluster, state=cluster.BORDER_NODE)

    def _node_added(self, node):
        """
        Method calculates for a newly added node, how it influences the current clustering.
        The node might become core, border, or even noise.

        :param node: The node that was just added
        """
        self.noise.add(node)
        neighbours = set(self.graph.get_neighbours(node=node, distance=self.cluster_distance))
        neighbours.add(node)
        self._edge_added(neighbours, new_node=node)

    @staticmethod
    def _expand_unchecked(unchecked, neighbours, checked=None):
        to_be_checked = set(neighbours) - checked
        unchecked.update(to_be_checked)
        checked.update(to_be_checked)

    def _init_cluster(self):
        """Perform initial clustering"""
        self.clusters = type(self.clusters)()
        # Avoid nodes for which a decision has been made:
        # - Core nodes can only belong to one cluster; once a node is a cluster
        #   core node, it cannot change state.
        # - Border nodes are treated when clusters are created, so we can skip them
        self.noise = set(self.graph)
        for node in self.graph:  # nodes from single iteration over graph
            if node in self.noise:
                neighbours = set(self.graph.get_neighbours(node=node, distance=self.cluster_distance))
                if len(neighbours) >= self.core_neighbours:
                    # node forms a new cluster
                    this_cluster = dengraph.cluster.DenGraphCluster(self.graph)
                    self.clusters.append(this_cluster)
                    self._add_node_to_cluster(
                        node=node,
                        cluster=this_cluster,
                        state=this_cluster.CORE_NODE
                    )
                    outstanding_nodes = set()  # nodes which still need categorizing
                    connected_nodes = {node}  # nodes which need not be scheduled for categorizing again
                    outstanding_nodes.update(neighbours)
                    connected_nodes.update(neighbours)
                    while outstanding_nodes:
                        checking = outstanding_nodes.pop()
                        neighbours = set(self.graph.get_neighbours(
                            node=checking,
                            distance=self.cluster_distance
                        ))
                        if len(neighbours) >= self.core_neighbours:
                            self._add_node_to_cluster(
                                node=checking,
                                cluster=this_cluster,
                                state=this_cluster.CORE_NODE
                            )
                            self._expand_unchecked(outstanding_nodes, neighbours, connected_nodes)
                        else:
                            self._add_node_to_cluster(
                                node=checking,
                                cluster=this_cluster,
                                state=this_cluster.BORDER_NODE
                            )
        # sort clusters by length to reduce '__contains__' checks
        # having big clusters first means on average, searched elements are
        # more likely to be in earlier containers.
        self.clusters.sort(key=len)

    def __contains__(self, item):
        if isinstance(item, slice):
            return item.start in self and item.stop in self
        else:
            for cluster in self.clusters:
                if item in cluster:
                    return True
        return False

    def __len__(self):
        return sum(len(clstr) for clstr in self.clusters)

    def __getitem__(self, item):
        if item in self:
            return self.graph[item]
        else:
            # raise the appropriate error
            if isinstance(item, slice):
                raise dengraph.graph.NoSuchEdge  # Edge not in any Cluster
            raise dengraph.graph.NoSuchNode  # Node not in any Cluster

    def __setitem__(self, key, value):
        # add stuff to graph
        try:
            self.graph[key] = value
        except:
            raise
        else:
            if isinstance(key, slice):
                nodes = [key.start, key.stop]
                self._edge_added(nodes)
            else:
                self._node_added(key)
            self.clusters.sort(key=len)

    def __delitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            del self.graph[item]
            self._edge_removed(node=item.start)
            self._edge_removed(node=item.stop)
            try:
                cluster = self.core_cluster_for_node(core_node=item.start)
            except NoSuchCluster:
                try:
                    cluster = self.core_cluster_for_node(core_node=item.stop)
                except NoSuchCluster:
                    return
            self._check_cluster(nodes=[item.start, item.stop], core_cluster=cluster)
        else:
            neighbours = set(self.graph.get_neighbours(node=item, distance=self.cluster_distance))
            self._node_removed(node=item, neighbours=neighbours)
            del self.graph[item]

    def __iter__(self):
        for cluster in self.clusters:
            yield cluster

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            if (
                len(self) != len(other) or
                self.cluster_distance != other.cluster_distance or
                self.core_neighbours != other.core_neighbours
            ):
                return False
            elif self.noise != other.noise:
                return False
            else:
                return all(my_clst in other.clusters for my_clst in self.clusters)

    def __repr__(self):
        return '%s(cluster_distance=%s, core_neighbours=%s, clusters=%s, noise=%s)' % (
            self.__class__.__name__,
            self.cluster_distance,
            self.core_neighbours,
            dengraph.utilities.pretty.repr_container(self.clusters),
            dengraph.utilities.pretty.repr_container(self.noise),
        )

    def get_neighbours(self, node, distance=dengraph.graph.ANY_DISTANCE):
        raise NotImplementedError  # TODO: find closest nodes

#: alias to have a separate name for future optimizations
DenGraphO = DenGraphIO
