"""
reduce_close_points.py

Provides functionality to reduce/consolidate point clouds by merging nearby points
within a specified distance threshold and replacing them with their centroid.
"""


def reduce_close_points(points, distance_threshold_meters, haversine_func):
    """
    Reduce points by consolidating those within a specified distance.
    Points closer than distance_threshold_meters are merged using their centroid.
    
    Args:
        points: List of (lon, lat) tuples representing point coordinates
        distance_threshold_meters: Maximum distance (in meters) for consolidating points.
                                  Points within this distance are merged.
        haversine_func: Function to calculate haversine distance between two points.
                       Should accept (lat1, lon1, lat2, lon2) and return distance in meters.
    
    Returns:
        List of consolidated (lon, lat) tuples. Points within the threshold distance
        are replaced by their centroid coordinate.
    
    Example:
        >>> from utils.haversine_distance import haversine_distance
        >>> points = [(35.0, 31.0), (35.001, 31.001), (36.0, 32.0)]
        >>> reduced = reduce_close_points(points, 100, haversine_distance)
        >>> len(reduced) < len(points)  # Some points consolidated
        True
    """
    if not points:
        return points
    
    consolidated = []
    used = set()
    
    for i, (lon1, lat1) in enumerate(points):
        if i in used:
            continue
        
        # Find all points close to this point
        group = [(lon1, lat1)]
        used.add(i)
        
        for j in range(i + 1, len(points)):
            if j in used:
                continue
            lon2, lat2 = points[j]
            
            # Calculate haversine distance (pass points as tuples)
            distance = haversine_func((lat1, lon1), (lat2, lon2))
            
            if distance <= distance_threshold_meters:
                group.append((lon2, lat2))
                used.add(j)
        
        # Calculate centroid of the group
        avg_lon = sum(p[0] for p in group) / len(group)
        avg_lat = sum(p[1] for p in group) / len(group)
        consolidated.append((avg_lon, avg_lat))
    
    return consolidated
