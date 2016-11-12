from dengraph.quality.inter_intra import inter_cluster_mean_score


def davies_bouldin_score(clusters, graph):
    """
    The Davies-Bouldin score averages over all pairs of clusters. Therefore for each cluster, all
    different clusters are taken to first determine their sum of average distances of all instances
    within the two clusters to their respective centroid. This is normalised over the distance
    between the given centroids. For each pair, the maximum is determined.

    The target value for the Davies-Bouldin score is small, since this corresponds to dense but
    well separated clusters.

    :param clusters: The clusters to determine the Davies-Bouldin score for
    :param graph: The underlying graph that offers distance function
    :return: Calculated Davies-Bouldin score
    """
    if len(clusters) > 1:
        score_cache = {}
        means_cache = {}
        result = 0
        for cluster_1 in clusters:
            maximum_distance = 0
            for cluster_2 in clusters:
                if cluster_1 != cluster_2:
                    try:
                        means_cache[cluster_1]
                    except KeyError:
                        means_cache[cluster_1] = graph.distance.mean(list(cluster_1))
                        score_cache[cluster_1] = inter_cluster_mean_score(
                            cluster_1,
                            graph,
                            means_cache[cluster_1])
                    try:
                        means_cache[cluster_2]
                    except KeyError:
                        means_cache[cluster_2] = graph.distance.mean(list(cluster_2))
                        score_cache[cluster_2] = inter_cluster_mean_score(
                            cluster_2,
                            graph,
                            means_cache[cluster_2])

                    distance = (score_cache[cluster_1] + score_cache[cluster_2]) / \
                        graph.distance(means_cache[cluster_1], means_cache[cluster_2])
                    if distance > maximum_distance:
                        maximum_distance = distance
            result += maximum_distance
        return result / float(len(list(clusters)))
    raise ValueError
