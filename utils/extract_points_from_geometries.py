from shapely.geometry import Point

def extract_points_from_geometries(geometries):
    """
    Filters a list of Shapely geometries to return only Point objects.

    Args:
        geometries (list): A list of Shapely geometry objects.

    Returns:
        list: A new list containing only Shapely Point objects.
    """
    return [geom for geom in geometries if geom.geom_type == 'Point']