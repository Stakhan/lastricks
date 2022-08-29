"""
/!\\ This code has been designed to be used with laspy 1.7.x
"""

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


def is_within_worker(point, polygons, gpkg_as_mask=True):
    within_list = polygons.geometry[polygons.geometry.apply(point.within)]
    if gpkg_as_mask:
        return len(within_list.index) != 0
    else:
        return len(within_list.index) == 0

def new_class_from_gpkg(
    gpkg_filename,
    las_path,
    base_class,
    new_class,
    output_folder=None,
    output_suffix=None,
    gpkg_as_mask=True
):
    """Generates a new class based on an existing class and a set of polygons
       or multipolygons. If points from `base_class` are within the given
       geometries, they are assigned the `new_class`.
    """
    print(f"Opening {gpkg_filename}...")
    polygons = gpd.read_file(gpkg_filename)
    
    if las_path.is_file():
        new_class_from_gpkg_single_file(
            polygons,
            las_path,
            base_class,
            new_class,
            output_folder=output_folder,
            output_suffix=output_suffix,
            gpkg_as_mask=gpkg_as_mask
        )
    elif las_path.is_dir():
        las_paths = [p for p in las_path.iterdir() if p.is_file() and p.suffix == '.las']
        for i,path in enumerate(las_paths):
            startt = time.time()
            print(f"[{i+1}/{len(las_paths)}]")
            new_class_from_gpkg_single_file(
                polygons,
                path,
                base_class,
                new_class,
                output_folder=output_folder,
                output_suffix=output_suffix,
                gpkg_as_mask=gpkg_as_mask
            )
            print(f"-- Processing time: {timedelta(seconds=time.time()-startt)}")


def new_class_from_gpkg_single_file(
    polygons,
    las_filename,
    base_class,
    new_class,
    output_folder=None,
    output_suffix=None,
    gpkg_as_mask=True
):  
    lasfile = laspy.file.File(las_filename, mode='r')
    lasheader = lasfile.header

    base_class_mask = lasfile.classification == base_class
    points_coords = pd.DataFrame(data={'x': lasfile.x[base_class_mask], 'y': lasfile.y[base_class_mask]})
    
    lasfile_hold = Polygon([
        (lasheader.min[0], lasheader.min[1]),
        (lasheader.max[0], lasheader.min[1]),
        (lasheader.max[0], lasheader.max[1]),
        (lasheader.min[0], lasheader.max[1])
        ])

    zone_mask = polygons.geometry.apply(lasfile_hold.intersects)

    points = gpd.points_from_xy(points_coords.x, points_coords.y, crs="EPSG:28992")
    pts_idxs = np.where(base_class_mask)[0]
    modified_classif = lasfile.classification

    pool = mp.ProcessPool(processes=mp.cpu_count())
    print("Running parallel process...")
    within_mask = pool.map(partial(is_within_worker, polygons=polygons[zone_mask], gpkg_as_mask=gpkg_as_mask), points)
    print("Done.")

    modified_classif[ pts_idxs[within_mask] ] = new_class

    # Managing output folder
    if not output_folder:
        output_folder = Path(lasfile.filename).parent
    else:
        output_folder = output_folder
    
    # Managing output suffix 
    if (Path(output_folder) / las_filename).exists() and not output_suffix:
        output_suffix =  "_new_class"
    elif not output_suffix:
        output_suffix = ''
    else:
        output_suffix = output_suffix
    
    print(f"Saving result to {output_folder / (Path(las_filename).stem+output_suffix+Path(las_filename).suffix)}")
    output_lasfile = laspy.file.File(
        output_folder / (Path(las_filename).stem+output_suffix+Path(las_filename).suffix),
        mode = "w",
        header = lasfile.header
    )
    output_lasfile.points = lasfile.points
    output_lasfile.classification = modified_classif
    output_lasfile.close()

    lasfile.close()