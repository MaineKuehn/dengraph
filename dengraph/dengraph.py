import collections
import dengraph.graph
import dengraph.cluster


class DenGraphIO(dengraph.graph.Graph):
    """
    Density Graph allowing for Overlap and Incremental updates.
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
        self._init_cluster()

    def _init_cluster(self):
        """Perform initial cluster"""
        self.clusters = type(self.clusters)()
        # Avoid nodes for which a decision has been made:
        # - Core nodes can only belong to one cluster; once a node is a cluster
        #   core node, it cannot change state.
        # - Junk can NEVER be close to core or border nodes, so it will never
        #   show up again as neighbour.
        # - Border nodes may belong to multiple clusters, we WANT to inspect
        #   them again for each cluster.
        finalized = set()
        for node in self.graph:  # nodes from single iteration over graph
            if node in finalized:
                continue
            neighbours = self.graph.get_neighbours(node)
            # We haven't seen it, so it cannot be touched by any existing
            # cluster. If it's a core node, it MUST form a new cluster.
            # If it's not a core node, either a core will claim it or it's
            # junk. We just leave it to be claimed or remain junk.
            if len(neighbours) >= self.core_neighbours:
                finalized.add(node)
                this_cluster = dengraph.cluster.DenGraphCluster(self.graph)
                this_cluster.categorize_node(node, this_cluster.CORE_NODE)
                # stack of neighbours we must inspect
                # any neighbour belongs to the cluster, by definition.
                unchecked = collections.deque(neighbours)
                # A core's neighbour is automatically part of the cluster.
                # We recurse neighbour-to-neighbour to find the entire cluster.
                while unchecked:  # nodes from recursive iteration over cluster
                    neighbour = unchecked.popleft()
                    neighbours = self.graph.get_neighbours(neighbour)
                    # This neighbour is another center which extends the
                    # cluster, so all its neighbours are at least border nodes.
                    if len(neighbours) >= self.core_neighbours:
                        finalized.add(node)
                        this_cluster.categorize_node(node, this_cluster.CORE_NODE)
                        unchecked.extend(nnode for nnode in neighbours if nnode not in finalized)
                    else:
                        this_cluster.categorize_node(node, this_cluster.BORDER_NODE)
                self.clusters.append(this_cluster)
        # sort clusters by length to reduce '__contains__' checks
        # having big clusters first means on average, searched elements are
        # more likely to be in earlier containers.
        self.clusters.sort(key=lambda clstr: len(clstr))

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
        raise NotImplementedError  # TODO: insert/update edge

    def __delitem__(self, item):
        # a:b -> slice -> edge
        if isinstance(item, slice):
            raise NotImplementedError  # TODO: remove edge
        else:
            raise NotImplementedError  # TODO: remove node

    def __iter__(self):
        for node in self.graph:
            for cluster in self.clusters:
                if node in cluster:
                    yield node
                    break

    def get_neighbours(self, node, distance):
        raise NotImplementedError  # TODO: find closest nodes

    def insert_node(self, node, *args, **kwargs):
        raise NotImplementedError

    def remove_node(self, node, *args, **kwargs):
        raise NotImplementedError

    def insert_edge(self, node, *args, **kwargs):
        raise NotImplementedError

    def remove_edge(self, node, *args, **kwargs):
        raise NotImplementedError

    def modify_edge(self, node, *args, **kwargs):
        raise NotImplementedError
