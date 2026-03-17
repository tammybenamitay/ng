import random
import math
from shapely.geometry import Point

def polygons_to_random_points(polygons, density=0.001, spacing_meters=None):
    """Convert polygon interiors into points.

    This helper supports two useful modes:

    1) **Density-based** (legacy): generate an approximate number of random points based on polygon area.
       - `density` is interpreted as points per square degree.
       - Higher values produce more points.

    2) **Grid-spacing (meters)**: generate a grid of points inside each polygon where each point is
       approximately `spacing_meters` apart (in both latitude and longitude directions).
       - This is the behavior you requested: ``spacing_meters=50`` produces points spaced ~50m apart.

    Args:
        polygons (list): List of Shapely Polygon objects.
        density (float): Point density (points per square degree). Used only when `spacing_meters` is None.
        spacing_meters (float|None): If provided, overrides `density` and generates points on an approx.
            `spacing_meters` grid within each polygon.

    Returns:
        list: List of Shapely Point objects inside the input polygons.
    """

    random_points = []

    for polygon in polygons:
        minx, miny, maxx, maxy = polygon.bounds

        if spacing_meters is not None and spacing_meters > 0:
            # Convert meters to degrees based on latitude (approximate). 1 degree latitude ~ 111,320 meters.
            lat_center = (miny + maxy) / 2.0
            meters_per_degree_lat = 111_320
            meters_per_degree_lon = 111_320 * math.cos(math.radians(lat_center))

            dx = spacing_meters / meters_per_degree_lon
            dy = spacing_meters / meters_per_degree_lat

            if dx <= 0 or dy <= 0:
                continue

            # Generate a grid of points spaced by approximately spacing_meters
            x = minx
            while x <= maxx:
                y = miny
                while y <= maxy:
                    pt = Point(x, y)
                    if polygon.contains(pt):
                        random_points.append(pt)
                    y += dy
                x += dx

        else:
            # Legacy behavior: random points based on density (points per square degree)
            poly_area = polygon.area
            num_points = max(1, int(poly_area * density))

            points_in_polygon = 0
            attempts = 0
            max_attempts = num_points * 10  # Prevent infinite loop

            while points_in_polygon < num_points and attempts < max_attempts:
                random_x = random.uniform(minx, maxx)
                random_y = random.uniform(miny, maxy)
                random_point = Point(random_x, random_y)

                if polygon.contains(random_point):
                    random_points.append(random_point)
                    points_in_polygon += 1

                attempts += 1

    return random_points
