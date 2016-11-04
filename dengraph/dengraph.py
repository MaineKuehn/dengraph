# -*- coding: utf-8 -*-
from __future__ import absolute_import
import dengraph.graph
import dengraph.cluster
import dengraph.utilities.pretty


class NoSuchCluster(Exception):
    pass


class DenGraphIO(dengraph.graph.Graph):
    """
    Density Graph allowing for Overlap and Incremental updates.

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
        self._finalized_cores = set()
        self._init_cluster()

    def _merge_clusters(self, base_cluster, cluster):
        base_cluster += cluster
        if base_cluster == cluster:
            return base_cluster
        try:
            self.clusters.remove(cluster)
        except ValueError:
            pass
        return base_cluster

    def _current_core_cluster(self, core_node):
        """
        Method determines the current clusters a node belongs to and is labeled as core node.

        :param core_node: the core node to check cluster for
        :return: Cluster
        :raise: NoSuchCluster
        """
        for cluster in self.clusters:
            if core_node in cluster.core_nodes:
                return cluster
        raise NoSuchCluster

    def _clusters_for_node(self, node):
        for cluster in self.clusters:
            if node in cluster:
                yield cluster

    def _add_node_to_cluster(self, node, cluster, state):
        cluster.categorize_node(node, state)
        self.noise.discard(node)
        self._finalized_cores.add(node)

    def _test_change_to_core(self, node):
        """
        Method determines if a given node does become a core node. This method returns False,
        if the node is already a core node.

        :param node: The node to check
        :return: True, if node changes to core node, False otherwise
        """
        result = False
        # determine the neighbours of current node
        neighbours = self.graph.get_neighbours(node, self.cluster_distance)
        try:
            cluster = self._current_core_cluster(core_node=node)
        except NoSuchCluster:
            result = len(neighbours) >= self.core_neighbours
            cluster = None
        # return the current result and also the neighbours for further reference
        return result, cluster, neighbours

    def _test_change_from_core(self, node):
        result = False
        neighbours = self.graph.get_neighbours(node, self.cluster_distance)
        try:
            cluster = self._current_core_cluster(core_node=node)
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
            clusters = self._clusters_for_node(node=node)
            if len(list(clusters)) <= 1:
                self.noise.add(node)
                self._finalized_cores.discard(node)
        try:
            self.clusters.remove(cluster)
        except ValueError:
            pass

    def _edge_removed(self, node, base, removed=False):
        print("removing edge from %s to %s" % (node, base))
        is_downgraded, cluster, neighbours = self._test_change_from_core(node=node)
        if is_downgraded:
            self._add_node_to_cluster(node=node, cluster=cluster, state=cluster.BORDER_NODE)
        if cluster:
            if len(cluster.core_nodes) == 0:
                # remove cluster
                self._cluster_removed(cluster=cluster)
            if base in cluster:
                checked = set(neighbours + [base])
                unchecked = set(neighbours)
                current_cores = set()
                if not is_downgraded:
                    current_cores.add(node)
                current_borders = set()
                while unchecked:
                    checking = unchecked.pop()
                    if not removed and checking == base:
                        return
                    if checking in cluster:
                        neighbouring_neighbours = self.graph.get_neighbours(node=checking, distance=self.cluster_distance)
                        if len(neighbouring_neighbours) >= self.core_neighbours:
                            current_cores.add(checking)
                            self._expand_unchecked(unchecked=unchecked, neighbours=neighbouring_neighbours, checked=checked)
                        else:
                            current_borders.add(checking)
                missing_cores = cluster.core_nodes - current_cores
                missing_borders = set()
                print("[old] cores %s, borders %s" % (cluster.core_nodes, cluster.border_nodes))
                if removed:
                    missing_cores.discard(base)
                for core in missing_cores:
                    degrades, cluster, neighbours = self._test_change_from_core(node=core)
                    if degrades:
                        missing_cores.discard(core)
                        missing_borders.add(core)
                    else:
                        missing_borders.update(set(neighbours) - missing_cores)
                missing_borders.discard(base)
                left = cluster.core_nodes.union(cluster.border_nodes) - current_cores - current_borders - missing_cores - missing_borders
                if removed:
                    left.discard(base)
                print("[new] cores %s, borders %s" % (current_cores, current_borders))
                if len(current_cores) == 0:
                    self._cluster_removed(cluster=cluster)
                else:
                    cluster.core_nodes = current_cores
                    cluster.border_nodes = current_borders
                if len(missing_cores) > 0:
                    this_cluster = dengraph.cluster.DenGraphCluster(graph=self.graph)
                    self.clusters.append(this_cluster)
                    this_cluster.core_nodes = missing_cores
                    this_cluster.border_nodes = missing_borders
                else:
                    for node in missing_borders:
                        if len(list(self._clusters_for_node(node=node))) == 0:
                            self.noise.add(node)
                # update noise
                for node in left:
                    clusters = self._clusters_for_node(node=node)
                    if len(list(clusters)) == 0:
                        self.noise.add(node)

    def _node_removed(self, node, neighbours, clusters):
        if node in self.noise:
            # nothing needs to be done here... just remove from noise
            self.noise.discard(node)
        else:
            self._finalized_cores.discard(node)
            for neighbour in neighbours:
                del self.graph[neighbour:node]
                self._edge_removed(node=neighbour, base=node, removed=True)

    def _merge_neighbours(self, neighbours, cluster):
        for neighbour in neighbours:
            try:
                neighbouring_cluster = self._current_core_cluster(core_node=neighbour)
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
        neighbours = self.graph.get_neighbours(node=node, distance=self.cluster_distance)
        self._edge_added(neighbours + [node], new_node=node)

    def _expand_unchecked(self, unchecked, neighbours, checked=None):
        to_be_checked = set(neighbours) - checked
        unchecked.update(to_be_checked)
        checked.update(to_be_checked)

    def _init_cluster(self):
        """Perform initial cluster"""
        self.clusters = type(self.clusters)()
        # Avoid nodes for which a decision has been made:
        # - Core nodes can only belong to one cluster; once a node is a cluster
        #   core node, it cannot change state.
        # - Border nodes are treated when clusters are created, so we can skip them
        self.noise = set(self.graph)
        for node in self.graph:  # nodes from single iteration over graph
            if node in self.noise:
                neighbours = self.graph.get_neighbours(node=node, distance=self.cluster_distance)
                if len(neighbours) >= self.core_neighbours:
                    unchecked = set()
                    checked = set([node])
                    this_cluster = dengraph.cluster.DenGraphCluster(self.graph)
                    self.clusters.append(this_cluster)
                    self._add_node_to_cluster(node=node, cluster=this_cluster, state=this_cluster.CORE_NODE)
                    self._expand_unchecked(unchecked, neighbours, checked)
                    while unchecked:
                        checking = unchecked.pop()
                        neighbours = self.graph.get_neighbours(node=checking, distance=self.cluster_distance)
                        if len(neighbours) >= self.core_neighbours:
                            self._add_node_to_cluster(node=checking, cluster=this_cluster, state=this_cluster.CORE_NODE)
                            self._expand_unchecked(unchecked, neighbours, checked)
                        else:
                            self._add_node_to_cluster(node=checking, cluster=this_cluster, state=this_cluster.BORDER_NODE)
        # sort clusters by length to reduce '__contains__' checks
        # having big clusters first means on average, searched elements are
        # more likely to be in earlier containers.
        self.clusters.sort(key=lambda clstr: len(clstr))

    def __contains__(self, item):
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
            self.clusters.sort(key=lambda clstr: len(clstr))

    def __delitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            del self.graph[item]
            self._edge_removed(node=item.start, base=item.stop)
        else:
            neighbours = self.graph.get_neighbours(node=item, distance=self.cluster_distance)
            clusters = self._clusters_for_node(item)
            self._node_removed(node=item, neighbours=neighbours, clusters=clusters)
            del self.graph[item]

    def __iter__(self):
        for node in self.graph:
            for cluster in self.clusters:
                if node in cluster:
                    yield node
                    break

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

    def get_neighbours(self, node, distance):
        raise NotImplementedError  # TODO: find closest nodes

#: alias to have a separate name for future optimizations
DenGraphO = DenGraphIO
