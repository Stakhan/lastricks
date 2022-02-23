import laspy
import shutil
import pytest
import rasterio
import numpy as np

"""
These fixtures are similar to the ones in
`test.common_fixtures` but they use laspy 2.x
"""

@pytest.fixture
def mock_las_v2(tmp_path):
    """Generates a small mock LAS file using laspy 2.x.

    Returns:
        pathlib.Path: path to generated LAS file 
    """
    filename = tmp_path / "test_data" / "mock.las"
    (tmp_path / "test_data").mkdir(exist_ok=True)

    allX = np.array([1, 2000, 3000, 5000, 6000, 6000])
    allY = np.array([1000, 0, 0, 2000, 2000, 3000])
    allZ = np.array([1001, 2000, 55000, 27000, 8000, 9000])

    Xmin = np.floor(np.min(allX))
    Ymin = np.floor(np.min(allY))
    Zmin = np.floor(np.min(allZ))
    Xmax = np.ceil(np.max(allX))
    Ymax = np.ceil(np.max(allY))
    Zmax = np.ceil(np.max(allZ))

    mock_hdr = laspy.LasHeader(version="1.2", point_format=1)
    mock_hdr.offsets = [0.0,0.0,0.0]
    mock_hdr.scales = [0.001,0.001,0.001]
    mock_hdr.mins = [Xmax,Ymax,Zmax]
    mock_hdr.maxs = [Xmax,Ymax,Zmax]

    mock_las = laspy.LasData(mock_hdr)

    mock_las.X = allX
    mock_las.Y = allY
    mock_las.Z = allZ

    mock_las.classification = [1, 1, 9, 9, 1, 1]

    mock_las.write(filename)

    yield filename

    shutil.rmtree(filename, ignore_errors=True)


@pytest.fixture
def folder_mock_las_v2(mock_las_v2):
    """Generates a folder containing several copies of a mock LAS file.

    Args:
        mock_las_v2 (pytest.fixture): the `common_fixtures_v2.mock_las_v2`  fixture

    Returns:
        pathlib.Path: path to the generated folder
    """
    mock_folder = mock_las_v2.parent / 'mock_folder'
    mock_folder.mkdir(exist_ok=True)
    for i in range(3):
        shutil.copy(mock_las_v2, mock_folder / f'mock_{i}.las')
        lasfile = laspy.read(mock_folder / f'mock_{i}.las')
        lasfile.X += i*5000
        lasfile.write(mock_folder / f'mock_{i}.las')
    
    yield mock_folder

    shutil.rmtree(mock_folder, ignore_errors=True)


@pytest.fixture
def mock_dtm(tmp_path):
    x = np.linspace(1, 6, 8)
    y = np.linspace(1, 3, 3)
    X, Y = np.meshgrid(x, y)
    Z = X + Y

    mock_file = rasterio.open(
        tmp_path / 'mock_dtm.tif',
        'w',
        driver='GTiff',
        height=Z.shape[0],
        width=Z.shape[1],
        count=1,
        dtype=Z.dtype
    )
    mock_file.write(Z, 1)
    mock_file.close()

    return  tmp_path / 'mock_dtm.tif'