def inter_cluster_mean_score(cluster, graph, mean=None):
    """
    The method is based on the calculation of distances for each sample in a given cluster to
    the specific centroid of cluster. If the centroid is not given by specifying mean, it is
    calculated with the distance function that is provided by graph.

    :param cluster: The cluster to determine the mean inter cluster score for
    :param graph: The underlying graph that offers a distance function
    :param mean: A precalculated centroid for given cluster
    :return: Mean distances within the given cluster to its centroid
    """
    distance = 0
    if cluster:
        if mean is None:
            mean = graph.distance.mean(list(cluster))
        for node in cluster:
            distance += graph.distance(mean, node)
        return distance / float(len(list(cluster)))
    raise ValueError


def intra_cluster_variance(clusters, graph):
    """
    The intra cluster variance, or the between-cluster sum of squares returns for all given clusters
    the sum of squared distances from their centroid to the overall centroid of the given graph.
    For distance calculation and determination of centroids the distance function provided by the
    given graph is used.

    :param clusters: The clusters to determine the squared sum for
    :param graph: The underlying graph that offers a distance function
    :return: Sum of intra cluster variances for all given clusters
    """
    mean = graph.distance.mean([node for cluster in clusters for node in cluster])
    result = 0
    for cluster in clusters:
        result += len(cluster) * graph.distance(graph.distance.mean(list(cluster)), mean)**2
    return result


def inter_cluster_variance(clusters, graph):
    """
    The inter cluster variance, or the within-cluster sum of squares returns for all given clusters
    the sum of squared distances of each sample within that cluster to the clusters centroid.
    The sum of those squared distances is returned. For distance calculation the distance function
    provided by the given graph is used.

    :param clusters: The clusters to determine the squared sum for
    :param graph: The underlying graph that offers a distance function
    :return: Sum of inter cluster variances for all given clusters
    """
    if len(clusters) > 0:
        result = 0
        for cluster in clusters:
            cluster_mean = graph.distance.mean(list(cluster))
            for node in cluster:
                result += graph.distance(cluster_mean, node)**2
        return result
    return float("inf")
