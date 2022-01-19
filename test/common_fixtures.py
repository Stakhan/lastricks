import laspy
import pytest
import shutil
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
    allX = np.array([1, 2000, 3000, 5000, 6000])
    allY = np.array([1000, 0, 0, 2000, 2000])
    allZ = np.array([10.0, 10.0, 11.0, 9.0, 12.0])

    Xmin = np.floor(np.min(allX))
    Ymin = np.floor(np.min(allY))
    Zmin = np.floor(np.min(allZ))

    test_las.header.offset = [Xmin,Ymin,Zmin]
    test_las.header.scale = [0.001,0.001,0.001]

    test_las.X = allX
    test_las.Y = allY
    test_las.Z = allZ

    test_las.classification = [1, 1, 2, 2, 1]

    test_las.close()

    yield filename

    shutil.rmtree(filename, ignore_errors=True)

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