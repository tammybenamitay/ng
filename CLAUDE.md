# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a geospatial clustering analysis project that uses HDBSCAN with Optuna optimization to cluster point and polygon geometries. The main workflow is in Jupyter notebooks (`ng4.ipynb`) with utility functions in the `utils/` package.

## Development Environment

- **Python Version**: 3.14.3
- **Virtual Environment**: `.venv/` (already configured with all dependencies)
- **Platform**: Windows (paths use `C:\` format)

## Key Dependencies

```
optuna          # Hyperparameter optimization for clustering parameters
hdbscan         # Density-based spatial clustering
folium          # Interactive map visualization
shapely         # Geometric operations (Point, Polygon, MultiPoint)
numpy, scipy    # Scientific computing
```

## Running the Code

Activate the virtual environment before running Python commands:

```bash
# Windows
call .venv\Scripts\activate.bat

# Run the Jupyter notebook
jupyter notebook ng4.ipynb
```

## Architecture

### Three-Scenario Clustering Pipeline

The core workflow compares three different approaches to incorporating polygon data into HDBSCAN clustering:

1. **Scenario 1 (Red)**: Clusters using only original points (100 points near true location)
2. **Scenario 2 (Green)**: Converts all polygons to grid-spaced points, then clusters
3. **Scenario 3 (Blue)**: Identifies high-frequency polygon overlap areas, converts those to dense points, then clusters

### Key Modules

| Module | Purpose |
|--------|---------|
| `generate_geospatial_dataset.py` | Creates synthetic data: 100 points (t-distribution, 0-20m radius) + 20 polygons (16 containing true location, 4 distant) |
| `optimize_and_cluster_geometries.py` | Uses Optuna to find optimal `min_samples` and `eps_meters` parameters, minimizing median cluster radius |
| `cluster_points_and_get_all_cluster_polygons.py` | Applies HDBSCAN with Haversine distance metric, returns convex hull polygons for each cluster |
| `find_most_frequent_polygon_area.py` | Grid-based frequency analysis (default 100m cells), returns cells where ≥80% of max polygon count intersect |
| `polygons_to_random_points.py` | Converts polygons to points using either grid-spacing (meters) or density-based random sampling |
| `display_geospatial_dataset.py` | Renders interactive Folium map with toggleable layers for all three scenarios |
| `haversine_distance.py` | Calculates geographic distances in meters between (lat, lon) tuples |

### Coordinate System

- All coordinates use **(longitude, latitude)** order internally
- The constant `DEGREES_PER_METER_LAT = 0.0000089` is used for meter-to-degree conversions
- Latitude adjustment for longitude degrees: `degrees_per_meter_lon = degrees_per_meter_lat / cos(radians(latitude))`

### HDBSCAN Configuration

The clustering uses a custom Haversine distance metric wrapper to handle the [lon, lat] array format:

```python
def metric_wrapper(a, b):
    # a, b are [lon, lat] arrays; convert to (lat, lon) tuples
    return haversine_distance((a[1], a[0]), (b[1], b[0]))
```

### Optimization Parameters

Default Optuna search ranges (configurable per scenario):
- `min_samples`: 5-20 (minimum points to form a cluster)
- `eps_meters`: 5.0-40.0 (cluster_selection_epsilon in meters)
- `n_trials`: 100 (optimization iterations)

## Output Files

- `clustering_comparison_map.html` - Interactive Folium map comparing all scenarios (auto-saved during notebook execution)

## Notebook Cell Structure

The main notebook (`ng4.ipynb`) follows this execution order:
1. Environment detection (local vs Google Colab)
2. Package installation and imports with `importlib.reload()` for development
3. Dataset generation
4. Point reduction configuration (optional)
5. Three scenario data preparation
6. Optuna optimization and clustering for each scenario
7. Interactive map visualization
8. Distance statistics calculations
