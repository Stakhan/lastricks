"""
/!\\ These tests are meant to be used with laspy 1.7.x
"""

import laspy
import pytest
import shutil
import rasterio
import numpy as np
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon

root_path = Path(__file__).parent.resolve()


@pytest.fixture
def mock_las(tmp_path):
    """Generates a small mock LAS file.

    Returns:
        pathlib.Path: path to generated LAS file 
    """
    filename = tmp_path / "test_data" / "mock.las"
    (tmp_path / "test_data").mkdir(exist_ok=True)

    test_las = laspy.file.File(filename, mode="w", header=laspy.header.Header())
    allX = np.array([1, 2000, 3000, 5000, 6000, 6000])
    allY = np.array([1000, 0, 0, 2000, 2000, 3000])
    allZ = np.array([1001, 2000, 55000, 27000, 8000, 9000])

    Xmin = np.floor(np.min(allX))
    Ymin = np.floor(np.min(allY))
    Zmin = np.floor(np.min(allZ))
    Xmax = np.ceil(np.max(allX))
    Ymax = np.ceil(np.max(allY))
    Zmax = np.ceil(np.max(allZ))

    test_las.header.offset = [Xmin,Ymin,Zmin]
    test_las.header.scale = [0.001,0.001,0.001]
    test_las.header.min = [Xmax,Ymax,Zmax]
    test_las.header.max = [Xmax,Ymax,Zmax]

    test_las.X = allX
    test_las.Y = allY
    test_las.Z = allZ

    test_las.classification = [1, 1, 2, 2, 1, 1]

    test_las.close()

    yield filename

    shutil.rmtree(filename, ignore_errors=True)


@pytest.fixture
def folder_mock_las(mock_las):
    """Generates a folder containing several copies of a mock LAS file.

    Args:
        mock_las (pytest.fixture): the `common_fixtures.mock_las`  fixture

    Returns:
        pathlib.Path: path to the generated folder
    """
    mock_folder = mock_las.parent / 'mock_folder'
    mock_folder.mkdir(exist_ok=True)
    for i in range(3):
        shutil.copy(mock_las, mock_folder / f'mock_{i}.las')
        lasfile = laspy.file.File(mock_folder / f'mock_{i}.las', mode='rw')
        lasfile.X += i*5000
        lasfile.close()
    
    yield mock_folder

    shutil.rmtree(mock_folder, ignore_errors=True)

@pytest.fixture
def mock_gpkg(tmp_path):
    """Generates a small mock GeoPackage file.

    Yields:
        pathlib.Path: path to generated GeoPackage file
    """
    filename = tmp_path / "test_data" / "mock.gpkg"
    (root_path / "test_data").mkdir(exist_ok=True)

    df = gpd.GeoDataFrame(geometry=[ Polygon([(0.5, 0.5), (0, 2), (2, 1)]) ])
    df.to_file(filename, driver="GPKG")

    yield filename

    shutil.rmtree(filename, ignore_errors=True)