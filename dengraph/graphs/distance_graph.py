from dengraph import graph


class DistanceGraph(graph.Graph):
    """
    Graph
    """
    def __init__(self, nodes, distance, symmetric=True):
        self._nodes = set(nodes)
        self.distance = distance
        self.symmetric = symmetric
        self._distance_values = {}

    def __contains__(self, node):
        return node in self._nodes

    def __len__(self):
        return len(self._nodes)

    def __getitem__(self, row_col):
        row, col = row_col
        if col > row and self.symmetric:
            col, row = row, col
        try:
            return self._distance_values[row, col]
        except KeyError:
            self._compute_element(row, col)
            return self._distance_values[row, col]

    def _compute_element(self, row, col, force=False):
        if not force and (row, col) in self._distance_values:
            return
        self._distance_values[row, col] = self.distance(self._nodes[row], self._nodes[col])
        if self._distance_values[row, col] > self._max:
            self._max = self._distance_values[row, col]
        if self._distance_values[row, col] < self._min:
            self._min = self._distance_values[row, col]

    def __iter__(self):
        return iter(self._nodes)

    def get_neighbours(self, node, distance):
        raise NotImplementedError

    def insert_node(self, node):
        self._nodes.add(node)

    def insert_edge(self, *args, **kwargs):
        raise TypeError('%s does not implement %s' % (self.__class__.__name__, 'insert_edge'))

    def remove_edge(self, *args, **kwargs):
        raise TypeError('%s does not implement %s' % (self.__class__.__name__, 'remove_edge'))

    def modify_edge(self, *args, **kwargs):
        raise TypeError('%s does not implement %s' % (self.__class__.__name__, 'modify_edge'))
