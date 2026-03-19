import numpy as np
import math
from shapely.geometry import Point
from .haversine_distance import haversine_distance # Import haversine

def calculate_median_cluster_radius_meters(cluster_points, central_lat):
    """
    Calculates the median Haversine distance of points within a cluster from their centroid.

    Args:
        cluster_points (list): A list of Shapely Point objects representing the cluster.
        central_lat (float): The central latitude of the dataset (kept for function signature consistency, not used for Haversine).

    Returns:
        float: The median Haversine distance of points from the centroid in meters, or 0 if no points.
    """
    if not cluster_points:
        return 0.0

    # Calculate centroid of the cluster
    lats = [p.y for p in cluster_points]
    lons = [p.x for p in cluster_points]
    centroid_lat = np.mean(lats)
    centroid_lon = np.mean(lons)
    centroid = (centroid_lat, centroid_lon)

    # Calculate Haversine distance from each point to the centroid
    distances = []
    for point in cluster_points:
        distances.append(haversine_distance((point.y, point.x), centroid))

    return np.median(distances)