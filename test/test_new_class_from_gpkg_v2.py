import sys
import laspy
import pytest
import numpy as np
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks.cleaning as ltc
from lastricks.cleaning.new_class_from_gpkg import is_within_worker
from common_fixtures_v2 import mock_las_v2, mock_gpkg, folder_mock_las_v2, mock_dtm
 
    
def test_mock_files_consistency(mock_las_v2, mock_gpkg):
    las = laspy.read(mock_las_v2)
    d = gpd.read_file(mock_gpkg)
    print(las.x[0], las.y[0])
    p =  Point(las.x[0], las.y[0])
    assert len(d.geometry[d.geometry.apply(p.within) == True].index) == 1

def test_new_class_from_gpkg(mock_las_v2, mock_gpkg):
    ncfg = ltc.NewClassFromGpkg(
                mock_gpkg,
                1,
                8
            )
    las = laspy.read(mock_las_v2)
    res_las = ncfg( las )
    assert res_las.classification[0] == 8

def test_new_class_from_gpkg_revert_mask(mock_las_v2, mock_gpkg):
    ncfg = ltc.NewClassFromGpkg(
                mock_gpkg,
                1,
                9,
                gpkg_as_mask=False
            )
    
    las = laspy.read(mock_las_v2)
    res_las = ncfg( las )
    assert res_las.classification[1] == 9
    assert res_las.classification[4] == 9

def test_ReclassifyAbove_wrong_type():
    dtm = -1
    with pytest.raises(TypeError) as e_info:
        ncfg = ltc.NewClassFromGpkg(
                True,
                1,
                9,
                gpkg_as_mask=False
            )

def test_is_within_worker(mock_gpkg):
    point_in = Point(0.5,1)
    point_out = Point(0,1)
    
    polygons = gpd.read_file(mock_gpkg)
    
    assert is_within_worker(point_in, polygons)
    assert not is_within_worker(point_out, polygons)
    assert not is_within_worker(point_in, polygons, gpkg_as_mask=False)
    assert is_within_worker(point_out, polygons, gpkg_as_mask=False)