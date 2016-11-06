from __future__ import print_function
import time
import math
from matplotlib import pyplot

from dengraph_examples.distributions import Circle2D
from dengraph.utilities.pretty import str_time
from dengraph.graphs import adjacency_graph, distance_graph
from dengraph.dengraph import DenGraphIO


color_range = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta']


if __name__ == "__main__":
    for distribution in (Circle2D,):
        for density in (1500, 500,):
            print('Clustering', distribution, 'density', density)
            # create points
            start_time = time.time()
            points = Circle2D(1.0, 0.1).get_density(density) + Circle2D(0.5, 0.1).get_density(density)
            done_time = time.time()
            print('Generated %6d  points in %s' % (len(points), str_time(done_time - start_time)))
            # create graph
            start_time = time.time()
            graph = adjacency_graph.AdjacencyGraph(
                distance_graph.DistanceGraph(
                    nodes=points,
                    distance=lambda point_a, point_b:
                        math.sqrt(
                            (point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2
                        )
                )
            )
            done_time = time.time()
            print('Generated %6d^2 edges in %s' % (len(points), str_time(done_time - start_time)))
            # deduce clustering settings
            neighbours = 20
            distance = 1.5 * math.sqrt(neighbours / (density * math.pi))
            # print('Clustering with %d neighbours, %.3f distance' % (neighbours, distance))
            # cluster graph
            start_time = time.time()
            dengraph = DenGraphIO(graph, core_neighbours=neighbours, cluster_distance=distance)
            done_time = time.time()
            print('Generated %6d cluster in %s' % (len(dengraph.clusters), str_time(done_time - start_time)))
            # plot points first, then clusters on top
            for datapoints, color in [(points, "#000000")] + [
                (cluster, color_range[idx % len(color_range)]) for idx, cluster in enumerate(dengraph.clusters)
            ]:
                xys = zip(*datapoints)
                pyplot.scatter(
                    x=xys[0],
                    y=xys[1],
                    c=color,
                )
            pyplot.show()
            continue
