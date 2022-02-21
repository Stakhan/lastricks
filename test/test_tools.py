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
from .common_fixtures import mock_las, mock_gpkg, folder_mock_las, mock_dtm
 
    
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
    assert res_lasfile.classification[0] == 8

def test_new_class_from_gpkg_folder(folder_mock_las, mock_gpkg):
    lt.new_class_from_gpkg(
        mock_gpkg,
        folder_mock_las,
        1,
        8,
        output_folder=folder_mock_las.parent,
        output_suffix="_wec",
        )
    
    for i in range(3):
        res_lasfile = laspy.file.File(folder_mock_las.parent / f"mock_{i}_wec.las", mode="r")
        if i == 0:
            assert res_lasfile.classification[0] == 8
        else:
            assert res_lasfile.classification[0] == 1

def test_new_class_from_gpkg_revert_mask(mock_las, mock_gpkg):
    lt.new_class_from_gpkg(
        mock_gpkg,
        mock_las,
        1,
        9,
        output_folder=mock_las.parent,
        output_suffix="_wec",
        gpkg_as_mask=False
        )
    
    res_lasfile = laspy.file.File(mock_las.parent / "mock_wec.las", mode="r")
    assert res_lasfile.classification[1] == 9
    assert res_lasfile.classification[4] == 9

