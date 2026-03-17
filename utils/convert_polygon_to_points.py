import random
from shapely.geometry import Point, MultiPoint, Polygon

def convert_polygon_to_points(polygon, num_interior_points=10, spread_factor_interior=1.0):
    """
    Extracts exterior coordinates of a Shapely Polygon as points and generates
    random interior points, returning a list of all these Shapely Point objects.
    The spread of interior points can be controlled by `spread_factor_interior`.

    Args:
        polygon (shapely.geometry.Polygon): The input Shapely Polygon object.
        num_interior_points (int, optional): The number of random interior points to generate.
                                             Defaults to 10.
        spread_factor_interior (float, optional): A factor to control the spread of interior points.
                                                  A value > 1.0 will spread points beyond the original
                                                  bounding box, < 1.0 will constrain them more. Defaults to 1.0.

    Returns:
        list: A list of Shapely Point objects.
    """
    extracted_points = []

    if polygon.geom_type == 'Polygon':
        for coord in polygon.exterior.coords:
            extracted_points.append(Point(coord[0], coord[1]))
    else:
        print(f"Warning: Expected a Polygon, but received {polygon.geom_type}. No exterior points extracted.")
        return []

    minx, miny, maxx, maxy = polygon.bounds

    center_x = (minx + maxx) / 2
    center_y = (miny + maxy) / 2

    half_width_x = (maxx - minx) / 2
    half_width_y = (maxy - miny) / 2

    scaled_half_width_x = half_width_x * spread_factor_interior
    scaled_half_width_y = half_width_y * spread_factor_interior

    points_generated = 0
    max_attempts = num_interior_points * 100

    while points_generated < num_interior_points and max_attempts > 0:
        rand_x = random.uniform(center_x - scaled_half_width_x, center_x + scaled_half_width_x)
        rand_y = random.uniform(center_y - scaled_half_width_y, center_y + scaled_half_width_y)
        temp_point = Point(rand_x, rand_y)

        if temp_point.intersects(polygon):
            extracted_points.append(temp_point)
            points_generated += 1
        max_attempts -= 1

    if points_generated < num_interior_points:
        print(f"Warning: Only generated {points_generated} interior points out of {num_interior_points} for the polygon.")

    return extracted_points