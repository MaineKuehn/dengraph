from __future__ import print_function
from dengraph.graphs.distance_graph import DistanceGraph
from dengraph.dengraph import DenGraphIO

# numeric data
sequence = (1, 2, 3, 4, 5, 10, 11, 13, 14, 15, 17, 22, 23, 24, 25, 28, 29, 30, 31)

# create graph based on element-to-element difference
graph = DistanceGraph(
    nodes=sequence, distance=lambda node_from, node_to: abs(node_from - node_to)
)

clusterings = []
for neighbours in range(1, 4):
    for distance in range(1, 4):
        dengraph = DenGraphIO(
            graph, cluster_distance=distance, core_neighbours=neighbours
        )
        clusterings.append((neighbours, distance, dengraph))


# Helpers for printing
def format_sequence(seq):
    fmt = ""
    for num in range(min(seq), max(seq) + 1):
        if num in sequence:
            fmt += "#"
        else:
            fmt += " "
    return fmt


def format_clustering(seq, dgraph):
    """Format by cluster key, e.g. '   aAAAa bBBB-CCCd'"""
    keys = {
        cluster: chr(ord("a") + idx)
        for idx, cluster in enumerate(
            sorted(dgraph.clusters, key=lambda clst: len(clst))
        )
    }
    fmt = ""
    for elem in range(min(seq), max(seq) + 1):
        elem_key = None
        for cluster in dgraph.clusters:
            if elem in cluster:
                if elem_key is None:
                    elem_key = (
                        keys[cluster]
                        if elem in cluster.border_nodes
                        else keys[cluster].upper()
                    )
                else:
                    fmt += "+"
                    break
        else:
            fmt += " " if elem_key is None else elem_key
    return fmt


if __name__ == "__main__":
    last_nbs = None
    for nbs, dist, dgrph in clusterings:
        if nbs != last_nbs:
            print("nbs-dst", format_sequence(sequence))
            last_nbs = nbs
        print("%3d %3d" % (nbs, dist), format_clustering(sequence, dgrph))
