import tqdm
import laspy
import numpy as np
import pandas as pd
import logging as log
import geopandas as gpd
import multiprocessing as mp

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

    def is_within_worker(point):
    	within_list = polygons.geometry[polygons.geometry.apply(point.within)]
    	return len(within_list.index) != 0

    pool = mp.Pool(processes=mp.cpu_count())
    print("Launching parallel process")
    within_mask = pool.map_async(is_within_worker, points)
    print("Running parallel process...")
    within_mask.wait()

    modified_classif[ pts_idxs[within_mask] ] = new_class

    # Managing output path
    if not output_folder:
        output_folder = Path(lasfile.filename).parent
    if (Path(output_folder) / las_filename).exists() and not output_suffix:
        output_suffix =  "new_class"
    
    print(f"Saving result to {output_folder / (Path(las_filename).stem+output_suffix)}")
    output_lasfile = laspy.file.File(
        output_folder / (Path(las_filename).stem+output_suffix),
        mode = "w",
        header = lasfile.header
    )
    output_lasfile.points = lasfile.points
    output_lasfile.classification = modified_classif
    output_lasfile.close()
