from __future__ import absolute_import
import dengraph.graph


def silhouette_score(clusters, graph):
    """
    The silhouette score is a measure how similar points within a cluster are compared to points
    in other clusters. The score considers each point with the given clusters and determines
    their average distance within their cluster as well as the minimum average distance to the
    other clusters. The value is normalised with the maximum of both values.

    The score itself reaches from -1 to 1 whereas -1 means, that the clustering is poor. A high
    silhouette score of one means all points are good matched to their own clusters.

    The silhouette score can be used with any distance metric.

    :param clusters: The clusters to determine the Silhouette score for
    :param graph: The underlying graph that offers distance function
    :return: Calculated Silhouette score
    """
    if len(clusters) > 0:
        score = 0
        for cluster in clusters:
            for node in cluster:
                distance_a = avg_inter_cluster_distance(node, cluster, graph)
                try:
                    distance_b = min(avg_intra_cluster_distances(node, clusters, graph))
                except ValueError:
                    distance_b = 0
                maximum = max(distance_a, distance_b) or 1e-10
                score += (distance_b - distance_a) / maximum
        return score / float(sum([len(cluster) for cluster in clusters]))
    raise ValueError


def avg_inter_cluster_distance(sample, cluster, graph):
    """
    The method returns the average distance from a given sample to all other nodes within the
    given cluster. For distance calculation the distance function provided by the given graph
    is used.

    :param sample: Sample within cluster from which avg distances are calculated
    :param cluster: The cluster to calculate distances for
    :param graph: The underlying graph that offers a distance function
    :return: Average distance from sample to all other nodes in the cluster
    """
    result = 0
    if sample in cluster:
        for node in cluster:
            try:
                result += graph[node:sample]
            except dengraph.graph.NoSuchEdge:
                result += graph.distance(node, sample)
        return result / float(len(list(cluster)) - 1)
    raise dengraph.graph.NoSuchNode


def avg_intra_cluster_distances(sample, clusters, graph):
    """
    The method returns a list of average cluster distances to all clusters the given sample does
    not belong to. For distance calculation the distance function provided by the given graph
    is used.

    :param sample: Sample from which the distance calculations to other clusters are performed to.
    :param clusters: The clusters to calculate the distances for, the one with sample is excluded
    :param graph: The underlying graph that offers a distance function
    :return: Average list of distances from sample to all clusters it does not belong to
    """
    results = []
    for cluster in clusters:
        if sample not in cluster:
            distance = 0
            for node in cluster:
                try:
                    distance += graph[node:sample]
                except dengraph.graph.NoSuchEdge:
                    distance += graph.distance(node, sample)
            distance /= float(len(list(cluster)))
            results.append(distance)
    return results
