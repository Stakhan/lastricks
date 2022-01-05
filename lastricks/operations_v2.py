import tqdm
import laspy
import numpy as np
import pandas as pd
import logging as log
import geopandas as gpd
from pathlib import Path
import pathos.multiprocessing as mp
from pathos.multiprocessing import ProcessingPool as Pool


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
    ope = NewClassFromGpkg(
        gpkg_filename,
        las_filename,
        base_class,
        new_class,
        output_folder=output_folder,
        output_suffix=output_suffix
    )

    ope()

    

    
def is_within_worker(NewClassFromGpkg_object):
    return NewClassFromGpkg_object.is_within_worker(NewClassFromGpkg_object.points)


class NewClassFromGpkg:

    def __init__(
        self,
        gpkg_filename,
        las_filename,
        base_class,
        new_class,
        output_folder=None,
        output_suffix=None
        ):
        self.polygons = gpd.read_file(gpkg_filename)
        self.lasfile = laspy.file.File(las_filename, mode='r')
        self.new_class = new_class
        
        base_class_mask = self.lasfile.classification == base_class
        
        points_coords = pd.DataFrame(data={'x': self.lasfile.x[base_class_mask], 'y': self.lasfile.y[base_class_mask]})
        self.points = gpd.points_from_xy(points_coords.x, points_coords.y, crs="EPSG:28992")
        
        self.pts_idxs = np.where(base_class_mask)[0]
        self.modified_classif = self.lasfile.classification

        # Managing output folder
        if not output_folder:
            self.output_folder = Path(lasfile.filename).parent
        else:
            self.output_folder = output_folder
        
        # Mananging output suffix 
        if (Path(output_folder) / las_filename).exists() and not output_suffix:
            self.output_suffix =  "new_class"
        elif not output_suffix:
            self.output_suffix = ''
        else:
            self.output_suffix = output_suffix

    def __call__(self):
        pool = Pool(mp.cpu_count())
        print("Launching parallel process")
        within_mask = pool.map(self.is_within_worker, self.points)
        print("Running parallel process...")
       # within_mask.wait()

        self.modified_classif[ self.pts_idxs[within_mask] ] = self.new_class

        self.write_result_to_las()

    def is_within_worker(self, point):
        within_list = self.polygons.geometry[polygons.geometry.apply(point.within)]
        return len(within_list.index) != 0

    def write_result_to_las(self):
        output_path = self.output_folder / (Path(self.las_filename).stem+self.output_suffix)
        
        print(f"Saving result to {output_path}")

        output_lasfile = laspy.file.File(
            output_path,
            mode = "w",
            header = self.lasfile.header
        )
        output_lasfile.points = self.lasfile.points
        output_lasfile.classification = self.modified_classif
        output_lasfile.close()