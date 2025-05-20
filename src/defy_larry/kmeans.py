"""K-Means clustering for defy-larry"""

from typing import Iterable

import numpy as np
from sklearn.cluster import KMeans


def get_centroids(items: Iterable[tuple[int, ...]], n: int) -> np.ndarray:
    """Return n cluster centers for the given items"""
    kmeans = KMeans(n_clusters=n)
    kmeans = kmeans.fit(items)

    return kmeans.cluster_centers_
