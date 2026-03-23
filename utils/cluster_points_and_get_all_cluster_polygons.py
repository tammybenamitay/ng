import hdbscan
import numpy as np
from shapely.geometry import Point, Polygon, MultiPoint
from .haversine_distance import haversine_distance # Import haversine
from .extract_points_from_geometries import extract_points_from_geometries # Import helper

def cluster_points_and_get_all_cluster_polygons(
    geometries,
    central_lat,
    min_samples,
    cluster_selection_epsilon_meters,
    verbose=True
):
    """
    Applies HDBSCAN clustering to Point geometries and returns detected clusters as polygons.
    Uses Haversine distance as the metric for HDBSCAN.

    Args:
        geometries (list): A list of Shapely geometry objects (Points and Polygons).
        central_lat (float): The central latitude of the dataset (for context, not scaling in this version).
        min_samples (int): The min_samples parameter for HDBSCAN.
        cluster_selection_epsilon_meters (float): The cluster_selection_epsilon (eps) parameter in meters for HDBSCAN.
        verbose (bool, optional): Whether to print diagnostic information. Defaults to True.

    Returns:
        list: A list of Shapely Polygon objects, each representing a detected cluster.
    """
    shapely_points = extract_points_from_geometries(geometries)

    if not shapely_points:
        if verbose:
            print("  WARNING: No points extracted from geometries")
        return []

    point_coords = np.array(
        [[point.x, point.y]
         for point in shapely_points]
    )

    if verbose:
        print(f"  Clustering {len(shapely_points)} points with min_samples={min_samples}, eps={cluster_selection_epsilon_meters}m")

    # Use a metric wrapper to swap [lon, lat] to (lat, lon)
    def metric_wrapper(a, b):
        return haversine_distance((a[1], a[0]), (b[1], b[0]))

    clusterer = hdbscan.HDBSCAN(
        min_samples=min_samples,
        cluster_selection_epsilon=cluster_selection_epsilon_meters,
        metric=metric_wrapper
    )

    # Fit the clustering model to point_coords
    cluster_labels = clusterer.fit_predict(point_coords)

    unique_labels = [label for label in np.unique(cluster_labels) if label != -1]
    noise_count = np.sum(cluster_labels == -1)

    if verbose:
        print(f"  HDBSCAN found {len(unique_labels)} cluster(s), {noise_count} noise points ({100*noise_count/len(shapely_points):.1f}%)")

    cluster_polygons = []
    dropped_clusters = 0
    for label in unique_labels:
        points_in_cluster = [shapely_points[i] for i, l in enumerate(cluster_labels) if l == label]
        if len(points_in_cluster) >= 3:
            multi_point = MultiPoint(points_in_cluster)
            cluster_polygons.append(multi_point.convex_hull)
        else:
            dropped_clusters += 1
            if verbose:
                print(f"  WARNING: Cluster {label} has only {len(points_in_cluster)} points (< 3), dropping")

    if dropped_clusters > 0 and verbose:
        print(f"  WARNING: Dropped {dropped_clusters} cluster(s) with < 3 points")

    if not cluster_polygons and verbose:
        print("  WARNING: No valid cluster polygons generated")

    return cluster_polygons