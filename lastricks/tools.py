import laspy
import numpy as np
import pandas as pd
import logging as log
import geopandas as gpd
from pathlib import Path
import pathos.multiprocessing as mp
from functools import partial


def is_within_worker(point, polygons):
    within_list = polygons.geometry[polygons.geometry.apply(point.within)]
    return len(within_list.index) != 0

def new_class_from_gpkg(
    gpkg_filename,
    las_filename,
    base_class,
    new_class,
    output_folder=None,
    output_suffix=None
):
    """Generates a new class based on an existing class and a set of polygons
       or multipolygons. If points from `base_class` are within the given
       geometries, they are assigned the `new_class`.
    """
    polygons = gpd.read_file(gpkg_filename)
    lasfile = laspy.file.File(las_filename, mode='r')

    base_class_mask = lasfile.classification == base_class
    points_coords = pd.DataFrame(data={'x': lasfile.x[base_class_mask], 'y': lasfile.y[base_class_mask]})
    
    points = gpd.points_from_xy(points_coords.x, points_coords.y, crs="EPSG:28992")
    pts_idxs = np.where(base_class_mask)[0]
    modified_classif = lasfile.classification

    pool = mp.ProcessPool(processes=mp.cpu_count())
    print("Launching parallel process")
    within_mask = pool.map(partial(is_within_worker, polygons=polygons), points)
    print("Running parallel process...")
    pool.close()

    modified_classif[ pts_idxs[within_mask] ] = new_class

    # Managing output folder
    if not output_folder:
        self.output_folder = Path(lasfile.filename).parent
    else:
        self.output_folder = output_folder
    
    # Mananging output suffix 
    if (Path(output_folder) / las_filename).exists() and not output_suffix:
        self.output_suffix =  "_new_class"
    elif not output_suffix:
        self.output_suffix = ''
    else:
        self.output_suffix = output_suffix
    
    print(f"Saving result to {output_folder / (Path(las_filename).stem+output_suffix+Path(las_filename).suffix)}")
    output_lasfile = laspy.file.File(
        output_folder / (Path(las_filename).stem+output_suffix+Path(las_filename).suffix),
        mode = "w",
        header = lasfile.header
    )
    output_lasfile.points = lasfile.points
    output_lasfile.classification = modified_classif
    output_lasfile.close()
