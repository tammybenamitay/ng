import optuna
import numpy as np
import hdbscan
from shapely.geometry import Point
from .extract_points_from_geometries import extract_points_from_geometries
from .calculate_median_cluster_radius_meters import calculate_median_cluster_radius_meters
from .haversine_distance import haversine_distance
from .cluster_points_and_get_all_cluster_polygons import cluster_points_and_get_all_cluster_polygons

def optimize_and_cluster_geometries(geometries, central_lat, n_trials=100, scenario_name="Default Scenario"):
    """
    Encapsulates the entire process of finding optimal HDBScan parameters using Optuna
    and then applying those parameters to identify all detected clusters.
    Uses Haversine distance as the metric for HDBSCAN.

    Args:
        geometries (list): A list of Shapely geometry objects (Points and Polygons).
        central_lat (float): The central latitude of the dataset (for context, not scaling in this version).
        n_trials (int, optional): The number of trials for Optuna optimization. Defaults to 500.
        scenario_name (str, optional): Name of the clustering scenario for logging. Defaults to "Default Scenario".

    Returns:
        tuple: (list of optimal_cluster_polygons, best_min_samples, best_eps_meters)
               Returns an empty list for polygons and 0 for parameters if no cluster is found.
    """

    def objective(trial):
        min_samples = trial.suggest_int('min_samples', 5, 20)  # Restrict range for tighter clusters
        eps_meters = trial.suggest_float('eps_meters', 5.0, 40.0)  # Restrict range for smaller clusters

        # Handle both Shapely geometries and coordinate tuples
        if geometries and isinstance(geometries[0], tuple) and len(geometries[0]) == 2:
            # Assume tuples are (lon, lat) and convert to Points accordingly
            shapely_points = [Point(lon, lat) for lon, lat in geometries]
        else:
            # Assume Shapely geometries
            shapely_points = extract_points_from_geometries(geometries)

        if not shapely_points:
            return float('inf')

        # For clustering, use [lon, lat] order for point_coords
        point_coords = np.array(
            [[point.x, point.y]
            for point in shapely_points]
        )

        # HDBSCAN with custom metric expects (lat, lon) tuples, so we must swap order in the metric
        def metric_wrapper(a, b):
            # a, b are [lon, lat] arrays; convert to (lat, lon) tuples
            return haversine_distance((a[1], a[0]), (b[1], b[0]))

        clusterer = hdbscan.HDBSCAN(min_samples=min_samples, cluster_selection_epsilon=eps_meters, metric=metric_wrapper)
        cluster_labels = clusterer.fit_predict(point_coords)

        unique_labels = [label for label in np.unique(cluster_labels) if label != -1]

        if not unique_labels:
            return float('inf')

        largest_cluster_label = -1
        max_cluster_size = 0
        for label in unique_labels:
            current_cluster_size = np.sum(cluster_labels == label)
            if current_cluster_size > max_cluster_size:
                max_cluster_size = current_cluster_size
                largest_cluster_label = label

        if largest_cluster_label == -1:
            return float('inf')

        largest_cluster_points = [
            shapely_points[i] for i, lbl in enumerate(cluster_labels)
            if lbl == largest_cluster_label
        ]

        median_radius_meters = calculate_median_cluster_radius_meters(largest_cluster_points, central_lat)
        return median_radius_meters

    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials)

    best_min_samples = study.best_trial.params['min_samples']
    best_eps_meters = study.best_trial.params['eps_meters']

    print(f"Optimization complete for {scenario_name}. Best min_samples: {best_min_samples}, best eps_meters: {best_eps_meters:.2f}, optimized median cluster radius: {study.best_trial.value:.2f} meters")

    # Ensure geometries are always a list of Points in (lon, lat) order
    if geometries and isinstance(geometries[0], tuple) and len(geometries[0]) == 2:
        processed_geometries = [Point(lon, lat) for lon, lat in geometries]
    else:
        processed_geometries = geometries

    all_optimal_cluster_polygons = cluster_points_and_get_all_cluster_polygons(
        processed_geometries,
        central_lat=central_lat,
        min_samples=best_min_samples,
        cluster_selection_epsilon_meters=best_eps_meters
    )

    return all_optimal_cluster_polygons, best_min_samples, best_eps_meters