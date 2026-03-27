"""
Convert polygons to geohash-based representative points.

This module takes Shapely polygon geometries and converts them to points
by encoding their locations as geohashes at a specified precision level,
then generating representative points (centroids) for each unique geohash cell.
"""

import geohash2
from shapely.geometry import Point, Polygon
import numpy as np


def get_geohash_cell_bounds(geohash_str):
    """
    Get the bounding box (lat/lon bounds) of a geohash cell.
    
    Args:
        geohash_str (str): A geohash string
        
    Returns:
        tuple: (min_lat, max_lat, min_lon, max_lon)
    """
    bbox = geohash2.bbox(geohash_str)
    # bbox returns (min_lat, min_lon, max_lat, max_lon)
    return (bbox[0], bbox[2], bbox[1], bbox[3])


def geohash_centroid(geohash_str):
    """
    Get the centroid (center point) of a geohash cell.
    
    Args:
        geohash_str (str): A geohash string
        
    Returns:
        tuple: (lat, lon) of the geohash cell center
    """
    bbox = geohash2.bbox(geohash_str)
    # bbox returns (min_lat, min_lon, max_lat, max_lon)
    min_lat, min_lon, max_lat, max_lon = bbox[0], bbox[1], bbox[2], bbox[3]
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    return (center_lat, center_lon)


def sample_points_from_polygon(polygon, num_samples=20):
    """
    Generate representative points from a polygon.
    Samples from the polygon boundary and interior.
    
    Args:
        polygon (Shapely Polygon): Input polygon
        num_samples (int): Number of sample points to generate
        
    Returns:
        list: List of (lat, lon) tuples representing points in the polygon
    """
    points = []
    
    # Add centroid
    centroid = polygon.centroid
    points.append((centroid.y, centroid.x))
    
    # Add points along the boundary
    boundary_samples = num_samples // 2
    if polygon.exterior is not None:
        boundary_length = polygon.exterior.length
        for i in range(boundary_samples):
            distance = (i / boundary_samples) * boundary_length
            point_on_boundary = polygon.exterior.interpolate(distance)
            points.append((point_on_boundary.y, point_on_boundary.x))
    
    # Add random interior points
    interior_samples = num_samples - len(points)
    minx, miny, maxx, maxy = polygon.bounds
    for _ in range(interior_samples):
        x = np.random.uniform(minx, maxx)
        y = np.random.uniform(miny, maxy)
        test_point = Point(x, y)
        if polygon.contains(test_point) or polygon.touches(test_point):
            points.append((y, x))  # (lat, lon)
    
    return points


def polygons_to_geohash_points(polygons, geohash_precision=9, num_samples_per_polygon=20):
    """
    Convert a list of Shapely polygons to geohash-based representative points.
    
    For each polygon:
    1. Sample representative points from the polygon
    2. Encode each point as a geohash at the specified precision
    3. Extract unique geohash cells
    4. Generate a representative point (centroid) for each unique geohash cell
    
    Args:
        polygons (list): List of Shapely polygon geometries
        geohash_precision (int): Precision level for geohash encoding (default: 9)
        num_samples_per_polygon (int): Number of sample points per polygon (default: 20)
        
    Returns:
        list: List of Shapely Point objects (lon, lat order) with unique geohash centroids
    """
    geohash_cells = set()  # Track unique geohashes
    
    # For each polygon, sample points and encode as geohashes
    for polygon in polygons:
        if polygon.is_empty or polygon.geom_type != 'Polygon':
            continue
        
        # Sample points from the polygon
        sample_points = sample_points_from_polygon(polygon, num_samples=num_samples_per_polygon)
        
        # Encode each sample point as a geohash and collect unique cells
        for lat, lon in sample_points:
            try:
                gh = geohash2.encode(lat, lon, precision=geohash_precision)
                geohash_cells.add(gh)
            except Exception:
                continue
    
    # Generate representative points (centroids) for each unique geohash cell
    result_points = []
    for geohash_str in geohash_cells:
        try:
            lat, lon = geohash_centroid(geohash_str)
            # Return as Shapely Point in (lon, lat) order to match other modules
            result_points.append(Point(lon, lat))
        except Exception:
            continue
    
    return result_points
