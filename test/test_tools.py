import sys
import laspy
import pytest
import numpy as np
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks as lt
from .common_fixtures import mock_las, mock_gpkg
 
    
def test_mock_files(mock_las, mock_gpkg):
    lasfile = laspy.file.File(mock_las)
    d = gpd.read_file(mock_gpkg)
    p =  Point(lasfile.x[0], lasfile.y[0])
    assert len(d.geometry[d.geometry.apply(p.within) == True].index) == 1

def test_new_class_from_gpkg(mock_las, mock_gpkg):
    lt.new_class_from_gpkg(
        mock_gpkg,
        mock_las,
        1,
        8,
        output_folder=mock_las.parent,
        output_suffix="_wec",
        )
    
    res_lasfile = laspy.file.File(mock_las.parent / "mock_wec.las", mode="r")
    input_lasfile = laspy.file.File(mock_las, mode="r")
    assert res_lasfile.classification[0] == 8