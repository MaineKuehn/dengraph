# -*- coding: utf-8 -*-
from __future__ import absolute_import
import collections
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

    def _check_for_merge(self, cluster, node):
        # Check all children for possible merging of clusters. If one of the neighbours is already
        # a core node, it means it is in another cluster. So both clusters are going to be merged.
        # If a node is not a core in another cluster, it means it will become a border node of
        # the current cluster.
        try:
            # Check for clusters that already contain the given node as a core node.
            # If no cluster can be found, an exception is raised and the node can be
            # categorized as a border node.
            cluster = self._merge_clusters(self._current_core_cluster(node), cluster)
        except NoSuchCluster:
            # Node was not part of a cluster, so it can be treated as a border node for the
            # current cluster
            self._add_node_to_cluster(node=node, cluster=cluster, state=cluster.BORDER_NODE)
        return cluster

    def _merge_all_neighbouring_clusters(self, core_node, neighbours):
        # we got a core node that was recently changed to core, so it might trigger merging of
        # neighbouring clusters it belongs to
        clusters = self._clusters_for_node(node=core_node)
        try:
            the_cluster = next(clusters)
        except StopIteration:
            # node is currently in no other cluster, so it builds a new one
            the_cluster = self._grow_cluster_from_seed(node=core_node, neighbours=neighbours)
        else:
            for cluster in clusters:
                the_cluster = self._merge_clusters(the_cluster, cluster)
            self._add_node_to_cluster(node=core_node,
                                      cluster=the_cluster,
                                      state=the_cluster.CORE_NODE)
        return the_cluster

    def _add_node_to_cluster(self, node, cluster, state):
        cluster.categorize_node(node, state)
        self.noise.discard(node)
        self._finalized_cores.add(node)

    def _grow_cluster_from_seed(self, node, neighbours, checked=None):
        checked = checked or set()
        # create a new cluster and save it to known clusters
        this_cluster = dengraph.cluster.DenGraphCluster(self.graph)
        self.clusters.append(this_cluster)
        # as the current node has been determined to become a core, save it to the current cluster
        self._add_node_to_cluster(node, this_cluster, this_cluster.CORE_NODE)
        # iterate over chained neighbours
        unchecked = set(neighbours)
        while unchecked:
            current_node = unchecked.pop()
            if current_node in checked:
                continue
            checked.add(current_node)
            if current_node in self._finalized_cores:
                # If we merged with an already existing node, it means we do not have to perform
                # further changes and can just drop operation. Neighbouring nodes should already
                # be marked as border nodes.)
                this_cluster = self._check_for_merge(cluster=this_cluster, node=current_node)
                continue
            # Whenever we inserted a new node that become a new core, it can also happen,
            # that the next neighbouring node becomes a core. Thus it is connecting to
            # another cluster.
            is_new_core, neighbouring_nodes = self._test_change_to_core(node=current_node)
            if is_new_core:
                # Next neighbouring node also builds a new core node, so we need to also
                # prepare its neighbouring nodes by recursing into the current method.
                self._add_node_to_cluster(current_node, this_cluster, this_cluster.CORE_NODE)
                unchecked.update([node for node in neighbouring_nodes if
                                    node not in checked and
                                    node != current_node])
            else:
                # However, at least each node belongs to the new clusters
                self._add_node_to_cluster(current_node, this_cluster, this_cluster.BORDER_NODE)
        return this_cluster

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
        # return the current result and also the neighbours for further reference
        return result, neighbours

    def _test_change_from_core(self, node):
        result = False
        neighbours = self.graph.get_neighbours(node, self.cluster_distance)
        try:
            self._current_core_cluster(core_node=node)
        except NoSuchCluster:
            # node was no core before, so False is returned
            pass
        else:
            result = len(neighbours) < self.core_neighbours
        return result, neighbours

    def _recluster(self, cluster):
        clustering = DenGraphIO(
            base_graph=cluster,
            cluster_distance=self.cluster_distance,
            core_neighbours=self.core_neighbours
        )
        self.noise.update(clustering.noise)
        self.clusters.remove(cluster)
        self.clusters.extend(clustering.clusters)

    def _remove_incremental_node(self, node, neighbours, clusters, former_node_type=None):
        if node in self.noise:
            # nothing needs to be done here... just remove from noise
            self.noise.discard(node)
            return
        try:
            cluster = next(clusters)
            if node in cluster.core_nodes:
                # node was a core node, so initiate reclustering
                self._finalized_cores.discard(node)
                cluster.core_nodes.discard(node)
                self._recluster(cluster=cluster)
            else:
                # node has just been a border node, so remove from current clusters
                cluster.border_nodes.discard(node)
                for cluster in clusters:
                    cluster.border_nodes.discard(node)
        except StopIteration:
            pass
        self.clusters.sort(key=lambda clstr: len(clstr))
        # also check each of the nodes neighbours for downgrading
        for neighbour in neighbours:
            downgrade_core, neighbouring_neighbours = self._test_change_from_core(neighbour)
            if downgrade_core:
                try:
                    cluster = self._current_core_cluster(neighbour)
                except NoSuchCluster:
                    pass
                else:
                    self._add_node_to_cluster(node=neighbour,
                                              cluster=cluster,
                                              state=cluster.BORDER_NODE)

    def _add_incremental_node(self, node):
        """
        Method calculates for a newly added node, how it influences the current clustering.
        The node might become core, border, or even junk.

        :param node: The node that was just added
        """
        self.noise.add(node)
        # determine neighbours of the node, if any and check its state
        is_new_core, neighbours = self._test_change_to_core(node=node)
        if is_new_core:
            # we got a core node and should insert it into the maybe already existing cluster
            self._merge_all_neighbouring_clusters(core_node=node, neighbours=neighbours)
        else:
            # The node might be a border node, or even noise, so check if additional edge
            # implicates the change of a node to a better class
            for neighbour in neighbours:
                # check if neighbour itself is a core node
                try:
                    cluster = self._current_core_cluster(neighbour)
                    # The currently checked node is a core node, so the added node should become
                    # a border node to the received cluster
                except NoSuchCluster:
                    # The neighbouring node is apparently a border node or noise.
                    # Noise nodes might exceed distance thresholds so that it exceeds current
                    # distance limits to become core.
                    # If it is a border node, it might belong to several clusters. This means,
                    # we might have to perform a merge of those clusters if we are exceeding
                    # current distance thresholds.
                    neighbour_is_new_core, neighbouring_neighbors = self._test_change_to_core(
                        node=neighbour)
                    if neighbour_is_new_core:
                        self._merge_all_neighbouring_clusters(core_node=node,
                                                              neighbours=neighbouring_neighbors)
                    # Node was a border or noise node, that is not going to change, so stop here.
                else:
                    self._add_node_to_cluster(node, cluster, cluster.BORDER_NODE)
                    # Nothing needs to happen from here, because the related core node cannot
                    # get better. And the node itself is a border node
        self.clusters.sort(key=lambda clstr: len(clstr))

    def _process_node(self, node):
        """
        Method checks for a single node if it is a new core node. If it is, neighbouring nodes
        are checked to get further core and border nodes.

        :param node: A node to be processed for clustering
        """
        # We haven't seen it, so it cannot be touched by any existing
        is_new_core, neighbours = self._test_change_to_core(node=node)
        # cluster. If it's a core node, it MUST form a new cluster.
        # If it's not a core node, either a core will claim it or it's
        # junk. We just leave it to be claimed or remain junk.
        if is_new_core:
            self._grow_cluster_from_seed(node=node, neighbours=neighbours)

    def _init_cluster(self):
        """Perform initial cluster"""
        self.clusters = type(self.clusters)()
        # Avoid nodes for which a decision has been made:
        # - Core nodes can only belong to one cluster; once a node is a cluster
        #   core node, it cannot change state.
        # - Border nodes are treated when clusters are created, so we can skip them
        self.noise = set(self.graph)
        for node in self.graph:  # nodes from single iteration over graph
            if node in self._finalized_cores:
                continue
            self._process_node(node)
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
            else:
                nodes = [key]
            for node in nodes:
                self._add_incremental_node(node)

    def __delitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            raise NotImplementedError  # TODO: remove edge
        else:
            neighbours = self.graph.get_neighbours(node=item, distance=self.cluster_distance)
            clusters = self._clusters_for_node(item)
            del self.graph[item]
            self._remove_incremental_node(node=item, neighbours=neighbours, clusters=clusters)

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
