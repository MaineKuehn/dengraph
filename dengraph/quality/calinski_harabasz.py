from dengraph.quality.inter_intra import inter_cluster_variance, intra_cluster_variance


def calinski_harabasz_score(clusters, graph):
    """
    The Calinski-Harabasz score (also called variance ratio criterion (VRC)) is based on two
    measures that evaluate separation and cohesion of clusters. Separation is considered by
    determining the intra-cluster variance and cohesion by determining inter-cluster variance.

    The aim is to find a number of cluster that maximise the score. Therefore, the higher the
    value the better.

    Note: The Calinski-Harabasz score also considers the existence of noise.

    :param clusters: The clusters to determine the Calinski-Harabasz score for
    :param graph: The underlying graph that offers distance function
    :return: Calculated Calinski-Harabasz score
    """
    if len(clusters) > 1:
        try:
            intra_inter = intra_cluster_variance(clusters, graph) / inter_cluster_variance(clusters, graph)
        except ZeroDivisionError:
            intra_inter = float("inf")
        result = intra_inter * ((len(list(graph)) - len(clusters)) / float(len(clusters) - 1))
        return result
    raise ValueError
