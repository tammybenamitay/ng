import math

def haversine_distance(point1, point2):
    """
    Calculates the Haversine distance between two geographical points in meters.

    Args:
        point1 (tuple): A tuple (latitude, longitude) for the first point.
        point2 (tuple): A tuple (latitude, longitude) for the second point.

    Returns:
        float: The distance between the two points in meters.
    """
    # Earth's radius in meters
    R = 6371000  # Mean radius of Earth in meters

    lat1, lon1 = point1
    lat2, lon2 = point2

    # Convert latitudes and longitudes from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance