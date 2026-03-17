import random
import math
import numpy as np
from shapely.geometry import Point, MultiPoint
from scipy.stats import t

# Define the constant, consistent with previous usage
DEGREES_PER_METER_LAT = 0.0000089

def generate_geospatial_dataset():
    true_location_lat = random.uniform(29.5, 33.5)
    true_location_lon = random.uniform(34.0, 36.0)

    degrees_per_meter_lat = DEGREES_PER_METER_LAT
    degrees_per_meter_lon = degrees_per_meter_lat / math.cos(math.radians(true_location_lat))

    print(f"Generated True Location: ({true_location_lat:.4f}, {true_location_lon:.4f})")
    print(f"Calculated Degrees per Meter (Lat): {degrees_per_meter_lat:.8f}")
    print(f"Calculated Degrees per Meter (Lon): {degrees_per_meter_lon:.8f}")

    all_generated_geometries = []

    most_points_close_to_true_location = []
    for _ in range(100):
        target_prob = 0.8
        df = 1
        t_quantile = t.ppf((1 + target_prob) / 2, df)
        scale = 20 / t_quantile
        dist_meters = t.rvs(df=df, loc=0, scale=scale)

        angle_rad = random.uniform(0, 2 * math.pi)
        offset_lat = dist_meters * degrees_per_meter_lat * math.sin(angle_rad)
        offset_lon = dist_meters * degrees_per_meter_lon * math.cos(angle_rad)
        new_point = Point(true_location_lon + offset_lon, true_location_lat + offset_lat)
        most_points_close_to_true_location.append(new_point)
    all_generated_geometries.extend(most_points_close_to_true_location)
    print(f"Generated {len(most_points_close_to_true_location)} 'most' points (0-20m bell curve).")

    diverse_polygons = []
    true_location_point = Point(true_location_lon, true_location_lat)

    for i in range(20):
        current_poly_center_lat = true_location_lat
        current_poly_center_lon = true_location_lon
        poly_max_vertex_dist_meters = random.uniform(100, 2000)

        if i < 16:
            poly_max_vertex_dist_meters = random.uniform(300, 2000)
            new_poly_center_lat = true_location_lat
            new_poly_center_lon = true_location_lon

        else:
            rand_dist_meters_center = random.uniform(3000, 5000)
            poly_max_vertex_dist_meters = random.uniform(100, 2000)

            rand_angle_rad_center = random.uniform(0, 2 * math.pi)
            offset_lat_center = rand_dist_meters_center * degrees_per_meter_lat * math.sin(rand_angle_rad_center)
            offset_lon_center = rand_dist_meters_center * degrees_per_meter_lon * math.cos(rand_angle_rad_center)

            new_poly_center_lat = true_location_lat + offset_lat_center
            new_poly_center_lon = true_location_lon + offset_lon_center

        num_vertices = random.randint(3, 8)
        vertices = []

        for _ in range(num_vertices):
            vertex_dist_meters = random.uniform(0, poly_max_vertex_dist_meters)
            vertex_angle_rad = random.uniform(0, 2 * math.pi)
            vertex_offset_lat = vertex_dist_meters * degrees_per_meter_lat * math.sin(vertex_angle_rad)
            vertex_offset_lon = vertex_dist_meters * degrees_per_meter_lon * math.cos(vertex_angle_rad)
            vertex_lat = new_poly_center_lat + vertex_offset_lat
            vertex_lon = new_poly_center_lon + vertex_offset_lon
            vertices.append((vertex_lon, vertex_lat))

        if len(vertices) >= 3:
            new_polygon = MultiPoint(vertices).convex_hull
            diverse_polygons.append(new_polygon)
    all_generated_geometries.extend(diverse_polygons)
    print(f"Generated {len(diverse_polygons)} 'diverse' polygons (16 containing true location, 4 non-intersecting).")

    return all_generated_geometries, true_location_lat, true_location_lon