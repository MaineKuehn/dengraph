class NoSuchEdge(Exception):
    pass


class Graph(object):
    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, a_b):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __contains__(self, item):
        raise NotImplementedError

    def get_neighbours(self, node, distance):
        raise NotImplementedError

    def insert_node(self, node):
        raise NotImplementedError

    # TODO:
    # -- intra distance
    # -- inter distance
