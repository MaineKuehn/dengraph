from __future__ import print_function
from dengraph.graphs.graph_io import csv_graph_reader, DistanceMatrixLiteral
from dengraph.dengraph import DenGraphIO

# distance matrix defined as CSV
time_since_last_call = """
Alfons Bernard Charlie Dirk Eduard Frank Gale Herbert
     0       2       7 None   None  None None      19
             0       9 None    121  None None     270
                     0   25   None   150 None     135
                          0      3    20   15     101
                                 0    13 None      27
                                       0 None      59
                                            0      42
                                                    0
""".strip()

# transform matrix to graph
call_graph = csv_graph_reader(
    time_since_last_call.splitlines(),  # literal to read
    max_distance=100,  # remove excessively large edges
    dialect=DistanceMatrixLiteral,  # space separated CSV
    symmetric=True,  # only half the matrix is set
)

friends = DenGraphIO(
    call_graph,
    core_neighbours=2,  # require at least one close friend
    cluster_distance=20,  # how often close friends call each other
).clusters

if __name__ == "__main__":
    print("Relation based on call statistics:")
    for idx, group in enumerate(friends):
        print("-- Superfriends", idx + 1, "--------")
        print("Close      :", ", ".join(group.core_nodes))
        print("Acquainted :", ", ".join(group.border_nodes))
