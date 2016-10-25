import dengraph.graph


class DenGraphCluster(dengraph.graph.Graph):
    """
    Cluster in a DenGraph
    """
    CORE_NODE = 1
    BORDER_NODE = 2

    def __init__(self, graph):
        self.graph = graph
        self.core_nodes = set()
        self.border_nodes = set()

    def categorize_node(self, node, state):
        if state == self.CORE_NODE:
            self.border_nodes.discard(node)
            self.core_nodes.add(node)
        elif state == self.BORDER_NODE:
            self.core_nodes.discard(node)
            self.border_nodes.add(node)

    def __len__(self):
        return len(self.core_nodes) + len(self.border_nodes)

    def __iter__(self):
        for node in self.border_nodes:
            yield node
        for node in self.core_nodes:
            yield node

    def __getitem__(self, a_b):
        return self.graph[a_b]

    def __contains__(self, node):
        return node in self.border_nodes or node in self.core_nodes

    def get_neighbours(self, node, distance):
        raise NotImplementedError
