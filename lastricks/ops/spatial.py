from __future__ import annotations
import laspy
import numpy as np
from pathlib import Path
from laspy import LasData
from shapely.geometry import Point, Polygon
from shapely.geometry.base import BaseGeometry

def spatial_query(las: LasData|list[LasData], geom: BaseGeometry) -> LasData:
    """Query points in bbox of given geometry.

    Args:
        las (LasData | list[LasData]): the LAS representation to extract
        the points from
        geom (BaseGeometry): The geometry used for the query

    Returns:
        LasData: LAS representation with extracted points
    """
    minx, miny, maxx, maxy = geom.bounds # (minx, miny, maxx, maxy)
    x, y = np.array(las.x), np.array(las.y)
    mask_x, mask_y = (minx <= x) * (x <= maxx), (miny <= y) * (y <= maxy)
    mask = mask_x * mask_y
    sub_las = LasData(las.header)
    sub_las.points = las.points[np.array(mask)]
    return sub_las

def get_bbox(laz_path: Path) -> Polygon:
        """Return bbox of given LAZ data

        Args:
            laz_path (Path): path to LAZ file

        Returns:
            Polygon: bbox of given file
        """
        with laspy.open(laz_path) as f:
            xmin, xmax, ymin, ymax = (
                f.header.mins[0], f.header.maxs[0],
                f.header.mins[1], f.header.maxs[1]
                )
        return Polygon([
            Point(xmin,ymin),
            Point(xmin,ymax),
            Point(xmax,ymax),
            Point(xmax,ymin)
        ])
