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

    lon_coords = np.arange(minx, maxx + grid_step_lon_deg, grid_step_lon_deg)
    lat_coords = np.arange(miny, maxy + grid_step_lat_deg, grid_step_lat_deg)

    if len(lon_coords) < 2 or len(lat_coords) < 2:
        print("Bounding box too small or grid_size_meters too large to form a grid. Returning overall union.")
        return [unary_union(polygons)]

    # Collect all grid cells and their frequencies
    grid_cells = []
    frequencies = []
    for i in range(len(lon_coords) - 1):
        for j in range(len(lat_coords) - 1):
            cell_minx, cell_maxx = lon_coords[i], lon_coords[i+1]
            cell_miny, cell_maxy = lat_coords[j], lat_coords[j+1]
            grid_cell = box(cell_minx, cell_miny, cell_maxx, cell_maxy)

            current_frequency = 0
            for poly in polygons:
                if grid_cell.intersects(poly):
                    current_frequency += 1
            grid_cells.append(grid_cell)
            frequencies.append(current_frequency)

    max_frequency = max(frequencies) if frequencies else 0
    threshold = max_frequency * 0.8  # 80% of max
    selected_cells = [cell for cell, freq in zip(grid_cells, frequencies) if freq >= threshold and freq > 0]

    print(f"Found {len(selected_cells)} area(s) with frequency >= 80% of max ({max_frequency}) intersecting polygons.")
    if selected_cells:
        return [cell for cell in selected_cells]
    else:
        return []