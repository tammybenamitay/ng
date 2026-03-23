import folium
import math
from shapely.geometry import Point, Polygon, LineString

# Define the constant, consistent with previous usage
DEGREES_PER_METER_LAT = 0.0000089

def display_geospatial_dataset(
    cluster_list,
    median_list,
    centroid_polygons,
    new_true_lat,
    new_true_lon,
    zoom_start=13
):
    """
    Displays geospatial clustering results on an interactive Folium map.

    Args:
        cluster_list (list): List of 3 cluster polygon lists:
                           [scenario_1_clusters, scenario_2_clusters, scenario_3_clusters]
        median_list (list): List of median radius values for each scenario.
        centroid_polygons (list): List of Shapely geometries (base dataset).
        new_true_lat (float): Latitude for map center.
        new_true_lon (float): Longitude for map center.
        zoom_start (int, optional): Initial zoom level. Defaults to 13.
    
    Map Layers (toggle in legend):
        - 📍 Base Dataset (Gray): Original polygons and points
        - 🔴 Scenario 1 (Red): Clustering with ORIGINAL POINTS ONLY
        - 🟢 Scenario 2 (Green): Clustering with ALL POLYGONS as RANDOM POINTS (density-controlled)
        - 🟠 Scenario 3 (Orange): Clustering with HIGH FREQUENCY AREAS as RANDOM POINTS
    """
    # Use an explicit pixel height so the map renders reliably in VS Code notebooks.
    m_display = folium.Map(
        location=[new_true_lat, new_true_lon],
        zoom_start=zoom_start,
        width="100%",
        height=600,
        control_scale=True,
    )

    # Layer 1: Base Dataset (gray) - Original polygons and points
    base_fg = folium.FeatureGroup(name="📍 Base Dataset (Original Geometries)", show=True).add_to(m_display)
    for geom in centroid_polygons:
        if geom.geom_type == 'Point':
            folium.CircleMarker(
                location=[geom.y, geom.x], 
                radius=2, 
                color='darkgray', 
                fill=True, 
                fill_color='darkgray',
                fill_opacity=0.6,
                weight=1,
                popup="Original Point"
            ).add_to(base_fg)
        elif geom.geom_type == 'Polygon':
            coords = [[p[1], p[0]] for p in list(geom.exterior.coords)]
            folium.Polygon(
                locations=coords, 
                color='lightgray', 
                fill=True, 
                fill_color='lightgray', 
                fill_opacity=0.15,
                weight=1,
                popup="Original Polygon"
            ).add_to(base_fg)

    # Scenario layers with distinct colors
    scenario_info = [
        ("🔴 Scenario 1: Original Points Only", "red", 0),
        ("🟢 Scenario 2: All Polygons → Random Points", "green", 1),
        ("🔵 Scenario 3: Clustered High Frequency Areas", "blue", 2),
        ("🩷 Scenario 4: Geohash-Based Aggregation", "magenta", 3),
        ("🟣 High Frequency Areas (Raw Polygons)", "purple", 4),
    ]

    for scenario_name, color, idx in scenario_info:
        if idx < len(cluster_list):
            # Show layer by default if there are any clusters to display
            show_layer = len(cluster_list[idx]) > 0
            cluster_fg = folium.FeatureGroup(name=scenario_name, show=show_layer).add_to(m_display)
            
            for cluster_geom in cluster_list[idx]:
                if cluster_geom.geom_type == 'Polygon':
                    coords_cluster = [[p[1], p[0]] for p in list(cluster_geom.exterior.coords)]
                    folium.Polygon(
                        locations=coords_cluster, 
                        color=color, 
                        fill=True, 
                        fill_color=color, 
                        fill_opacity=0.4,
                        weight=3,
                        popup=f"{scenario_name}"
                    ).add_to(cluster_fg)
                elif cluster_geom.geom_type == 'Point':
                    folium.CircleMarker(
                        location=[cluster_geom.y, cluster_geom.x], 
                        radius=6, 
                        color=color, 
                        fill=True, 
                        fill_color=color, 
                        fill_opacity=0.7,
                        weight=2,
                        popup=f"{scenario_name}"
                    ).add_to(cluster_fg)

    # Add true location marker and circle
    radius_meters = 20
    folium.Circle(
        location=[new_true_lat, new_true_lon],
        radius=radius_meters,
        color='yellow',
        fill=True,
        fill_color='yellow',
        fill_opacity=0.4,
        tooltip=f'{radius_meters}m radius'
    ).add_to(m_display)

    folium.Marker(
        location=[new_true_lat, new_true_lon],
        popup="True Location",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m_display)

    folium.LayerControl().add_to(m_display)

    return m_display