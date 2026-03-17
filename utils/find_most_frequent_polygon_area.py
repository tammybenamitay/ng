import numpy as np
import math
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

# Define the constant, consistent with previous usage
DEGREES_PER_METER_LAT = 0.0000089

def find_most_frequent_polygon_area(polygons, grid_size_meters=100):
    """
    Identifies the grid cell with the highest frequency of intersecting polygons and returns its area.

    Args:
        polygons (list): A list of Shapely Polygon objects.
        grid_size_meters (int, optional): The side length of a square grid cell in meters. Defaults to 100.

    Returns:
        float: The area in square degrees of the grid cell with the highest frequency of intersecting polygons,
               or 0.0 if no polygons are provided.
    """
    if not polygons:
        print("No polygons provided.")
        return []

    minx, miny, maxx, maxy = unary_union(polygons).bounds

    central_lat = (miny + maxy) / 2
    degrees_per_meter_lat = DEGREES_PER_METER_LAT
    degrees_per_meter_lon = degrees_per_meter_lat / math.cos(math.radians(central_lat))

    grid_step_lat_deg = grid_size_meters * degrees_per_meter_lat
    grid_step_lon_deg = grid_size_meters * degrees_per_meter_lon

    if grid_step_lat_deg == 0: grid_step_lat_deg = 0.00001
    if grid_step_lon_deg == 0: grid_step_lon_deg = 0.00001

    max_frequency = 0
    most_frequent_areas = []

    lon_coords = np.arange(minx, maxx + grid_step_lon_deg, grid_step_lon_deg)
    lat_coords = np.arange(miny, maxy + grid_step_lat_deg, grid_step_lat_deg)

    if len(lon_coords) < 2 or len(lat_coords) < 2:
        print("Bounding box too small or grid_size_meters too large to form a grid. Returning overall union.")
        return [unary_union(polygons)]

    for i in range(len(lon_coords) - 1):
        for j in range(len(lat_coords) - 1):
            cell_minx, cell_maxx = lon_coords[i], lon_coords[i+1]
            cell_miny, cell_maxy = lat_coords[j], lat_coords[j+1]
            grid_cell = box(cell_minx, cell_miny, cell_maxx, cell_maxy)

            current_frequency = 0
            for poly in polygons:
                if grid_cell.intersects(poly):
                    current_frequency += 1

            if current_frequency > max_frequency:
                max_frequency = current_frequency
                most_frequent_areas = [grid_cell]
            elif current_frequency == max_frequency and current_frequency > 0:
                most_frequent_areas.append(grid_cell)

    print(f"Found {len(most_frequent_areas)} area(s) with max frequency of {max_frequency} intersecting polygons.")
    if most_frequent_areas:
        return most_frequent_areas[0].area  # Return the area of the first (or only) most frequent grid cell
    else:
        return 0.0