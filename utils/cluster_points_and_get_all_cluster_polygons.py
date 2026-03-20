import hdbscan
import numpy as np
from shapely.geometry import Point, Polygon, MultiPoint
from .haversine_distance import haversine_distance # Import haversine
from .extract_points_from_geometries import extract_points_from_geometries # Import helper

def cluster_points_and_get_all_cluster_polygons(
    geometries,
    central_lat,
    min_samples,
    cluster_selection_epsilon_meters
):
    """
    Applies HDBSCAN clustering to Point geometries and returns detected clusters as polygons.
    Uses Haversine distance as the metric for HDBSCAN.

    Args:
        geometries (list): A list of Shapely geometry objects (Points and Polygons).
        central_lat (float): The central latitude of the dataset (for context, not scaling in this version).
        min_samples (int): The min_samples parameter for HDBSCAN.
        cluster_selection_epsilon_meters (float): The cluster_selection_epsilon (eps) parameter in meters for HDBSCAN.

    Returns:
        list: A list of Shapely Polygon objects, each representing a detected cluster.
    """
    shapely_points = extract_points_from_geometries(geometries)

    if not shapely_points:
        return []

    point_coords = np.array(
        [[point.x, point.y]
         for point in shapely_points]
    )

    # Initialize an hdbscan.HDBSCAN clustering model using Haversine distance
    clusterer = hdbscan.HDBSCAN(
        min_samples=min_samples,
        cluster_selection_epsilon=cluster_selection_epsilon_meters,
        metric=haversine_distance
    )

    # Fit the clustering model to point_coords
    cluster_labels = clusterer.fit_predict(point_coords)

    unique_labels = [label for label in np.unique(cluster_labels) if label != -1]

    cluster_polygons = []
    for label in unique_labels:
        points_in_cluster = [shapely_points[i] for i, l in enumerate(cluster_labels) if l == label]
        if len(points_in_cluster) >= 3:
            multi_point = MultiPoint(points_in_cluster)
            cluster_polygons.append(multi_point.convex_hull)

    return cluster_polygons