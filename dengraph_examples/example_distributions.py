# -*- coding: utf-8 -*-
from __future__ import print_function, division
import time
import math
from matplotlib import pyplot
import matplotlib

from dengraph_examples.distributions import Circle2D, Checkers, Moon, Gaussian
from dengraph.utilities.pretty import str_time
from dengraph.graphs import adjacency_graph, distance_graph
from dengraph.dengraph import DenGraphIO


def color_clusters(clusters):
    """
    Create colors for point collections in clusters

    :param clusters: DenGraph clusters to colorize
    :type clusters: tuple[:py:class:`~dengraph.cluster.DenGraphCluster`]
    :return: tuples of `(points, color)` for each cluster
    """
    border_pcs = []
    core_pcs = []
    for idx, cluster in enumerate(clusters):
        border_pcs.append(
            (
                cluster.border_nodes,
                tuple(
                    list(matplotlib.colors.hsv_to_rgb((idx / len(clusters), 1.0, 0.5)))
                    + [0.5]
                ),
            )
        )
        core_pcs.append(
            (
                cluster.core_nodes,
                matplotlib.colors.hsv_to_rgb((idx / len(clusters), 1.0, 1.0)),
            )
        )
    return border_pcs + core_pcs


def circles(density):
    return Circle2D(0.4, 0.04).get_density(density) + Circle2D(0.2, 0.02).get_density(
        density
    )


def dots(density):
    return (
        Gaussian((0.4, 0.35)).get_density(density)
        + Gaussian((0.4, -0.05)).get_density(density)
        + Gaussian((-0.1, 0.1)).get_density(density)
        + Gaussian((-0.3, -0.3)).get_density(density)
    )


def chess(density):
    return Checkers().get_density(density)


def moons(density):
    return Moon(radius_center=0.4, noise=0.03, center=(0.2, 0.1)).get_density(
        density
    ) + Moon(
        radius_center=0.4, noise=0.03, angular_center=math.pi, center=(-0.2, -0.1)
    ).get_density(
        density
    )


if __name__ == "__main__":
    generators = (circles, dots, chess, moons)
    densities = (5000, 3000, 1500, 500)
    fig, axes = pyplot.subplots(
        nrows=len(densities),
        ncols=len(generators),
        sharex=False,
        sharey=False,
        gridspec_kw={"hspace": 0.0, "wspace": 0.0, "top": 1.0, "bottom": 0.0},
        squeeze=False,
    )
    fig.set_size_inches(16.0, 12.0)
    for col_idx, distribution in enumerate(generators):
        for row_idx, density in enumerate(densities):
            print("Clustering", distribution.__name__, "density", density)
            # create points
            start_time = time.time()
            points = distribution(density)
            done_time = time.time()
            print(
                "Generated %6d  points in %s"
                % (len(points), str_time(done_time - start_time))
            )
            # create graph
            start_time = time.time()
            graph = adjacency_graph.AdjacencyGraph(
                distance_graph.DistanceGraph(
                    nodes=points,
                    distance=lambda point_a, point_b: math.sqrt(
                        (point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2
                    ),
                )
            )
            done_time = time.time()
            graph_time = done_time - start_time
            print("Generated %6d^2 edges in %s" % (len(points), str_time(graph_time)))
            # guess clustering settings
            # one percent of points make a cluster
            distance = 0.05
            neighbours = 0.666 * max(int(math.pi * density * (distance ** 2)), 1)
            # print('Clustering with %d neighbours, %.3f distance' %
            # (neighbours, distance))
            # cluster graph
            start_time = time.time()
            dengraph = DenGraphIO(
                graph, core_neighbours=neighbours, cluster_distance=distance
            )
            done_time = time.time()
            cluster_time = done_time - start_time
            print(
                "Generated %6d cluster in %s"
                % (len(dengraph.clusters), str_time(cluster_time))
            )
            # plotting
            this_axis = axes[row_idx][col_idx]
            this_axis.xaxis.set_ticklabels([])
            this_axis.yaxis.set_ticklabels([])
            this_axis.set_xticks([])
            this_axis.set_yticks([])
            this_axis.minorticks_off()
            # formatting
            this_axis.set_xlim(-0.65, 0.65)
            this_axis.set_ylim(-0.65, 0.65)
            # clustering settings
            this_axis.plot(
                *zip(
                    (0.6 - distance, -0.61),
                    (0.6 - distance, -0.6),
                    (0.6, -0.6),
                    (0.6, -0.61),
                )
            )
            this_axis.text(
                0.6,
                -0.6,
                u"η%d" % neighbours,
                ha="right",
                va="bottom",
            )
            # test/performance characteristics
            this_axis.text(
                0.02,
                0.98,
                u"In:  %s(ρ=%d, N=%d)" % (distribution.__name__, density, len(points)),
                ha="left",
                va="top",
                transform=this_axis.transAxes,
            )
            this_axis.text(
                0.02,
                0.02,
                u"Out: %3d cluster in %s"
                % (len(dengraph.clusters), str_time(cluster_time)),
                ha="left",
                va="bottom",
                transform=this_axis.transAxes,
            )
            # plot all points first, then lay clusters on top
            for datapoints, color in [(points, "#FFFFFF")] + color_clusters(
                dengraph.clusters
            ):
                if datapoints:
                    xys = zip(*datapoints)
                    this_axis.scatter(
                        x=xys[0],
                        y=xys[1],
                        c=color,
                    )
    pyplot.savefig("distributions_ex.svg")
    pyplot.show()
