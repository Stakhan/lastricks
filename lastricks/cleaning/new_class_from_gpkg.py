import time
import laspy
import numpy as np
import pandas as pd
import logging as log
import geopandas as gpd
from pathlib import Path
from functools import partial
from datetime import timedelta
import pathos.multiprocessing as mp
from shapely.geometry import Polygon
from .cleaning import CleaningProcess


def is_within_worker(point, polygons, gpkg_as_mask=True):
    within_list = polygons.geometry[polygons.geometry.apply(point.within)]
    if gpkg_as_mask:
        return len(within_list.index) != 0
    else:
        return len(within_list.index) == 0

class NewClassFromGpkg(CleaningProcess):
    def __init__(
        self,
        gpkg,
        base_class,
        new_class,
        gpkg_as_mask=True,
        bbox=None
    ):
        """Generates a new class based on an existing class and a set of polygons
        or multipolygons (provided as GeoPackage). If points from `base_class` are within the given
        geometries, they are assigned the `new_class`.

        Args:
            gpkg (str or pathlib.Path): GeoPackage containing a set of polygons
                that will serve as mask.
            base_class (int): class number of base class
            new_class (int): class number of new class
            gpkg_as_mask (bool, optional): When True, points from `base_class`
                inside the given geometries are assigned the `new_class`; when
                False, it is the points outside the given geometries that are
                assigned the `new_class`. Defaults to True.

        Raises:
            TypeError: when gpkg_filename is not provided in a sound manner.
        """
        if isinstance(gpkg, str) or isinstance(gpkg, Path):
                print(f"Opening {gpkg}...")
                self.polygons = gpd.read_file(gpkg, bbox=bbox)
        else:
            raise TypeError(f"gpkg should be a str or a pathlib.Path but got {type(gpkg).__name__} ")

        self.base_class   = base_class
        self.new_class    = new_class
        self.gpkg_as_mask = gpkg_as_mask


    def __call__(self, las):
        """Process a single python representation of a LAS/LAZ file.

        Args:
            las (laspy.LasData): LAS/LAZ file representation to process

        Returns:
            laspy.LasData: the resulting representation
        """  
        base_class_mask = np.array(las.classification) == self.base_class
        points_coords = pd.DataFrame(
            data={
                'x': np.array(las.x)[base_class_mask],
                'y': np.array(las.y)[base_class_mask]
                }
            )
        
        las_hold = Polygon([
            (las.header.mins[0], las.header.mins[1]),
            (las.header.maxs[0], las.header.mins[1]),
            (las.header.maxs[0], las.header.maxs[1]),
            (las.header.mins[0], las.header.maxs[1])
            ])

        zone_mask = self.polygons.geometry.apply(las_hold.intersects)

        points = gpd.points_from_xy(
            points_coords.x,
            points_coords.y,
            crs=self.polygons.crs.srs
            )
        pts_idxs = np.where(base_class_mask)[0]
        modified_classif = np.array(las.classification)

        pool = mp.ProcessPool(processes=mp.cpu_count())
        print("Running parallel process...")
        within_mask = pool.map(
            partial(
                is_within_worker,
                polygons=self.polygons[zone_mask],
                gpkg_as_mask=self.gpkg_as_mask
                ),
            points
        )
        print("Done.")

        modified_classif[ pts_idxs[within_mask] ] = self.new_class
        
        las.classification = modified_classif
        
        return las