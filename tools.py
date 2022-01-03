import tqdm
import laspy
import numpy as np
import pandas as pd
import geopandas as gpd
import multiprocessing as mp

def new_class_from_gpkg(gpkg_filename, las_filename, base_class, output_folder=None, output_suffix=None):
	"""Generates a new class based on an existing class and a set of polygons or multipolygons.
	   If a point from `base_class` are within the given geometries, they are assigned a new class.
	"""
	polygons = gpd.read_file(igpkg_filename)
	lasfile = laspy.file.File(las_filename, mode='r')

	water_points_mask = lasfile.classification == base_class
	points_coords = pd.DataFrame(data={'x': lasfile.x[water_points_mask], 'y': lasfile.y[water_points_mask]})

