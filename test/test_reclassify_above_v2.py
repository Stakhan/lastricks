"""
/!\\ These tests are meant to be used with laspy 2.x
"""
import sys
import laspy
import pytest
import rasterio
import numpy as np
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks.cleaning as ltc
from .common_fixtures_v2 import mock_las_v2, folder_mock_las_v2, mock_dtm
 

def test_ReclassifyAbove_from_path(mock_las_v2, mock_dtm):

    ra = ltc.ReclassifyAbove(
        mock_dtm,
        9,
        1,
        25.0
    )
    las = laspy.read(mock_las_v2)

    out_las = ra(las)

    assert out_las.classification[2] == 1
    assert out_las.classification[3] == 9

def test_ReclassifyAbove_from_DatasetReader(mock_las_v2, mock_dtm):
    dtm = rasterio.open(mock_dtm)

    ra = ltc.ReclassifyAbove(
        dtm,
        9,
        1,
        25.0
    )
    las = laspy.read(mock_las_v2)
    
    out_las = ra(las)

    assert out_las.classification[2] == 1
    assert out_las.classification[3] == 9

def test_ReclassifyAbove_wrong_type():
    dtm = -1
    with pytest.raises(TypeError) as e_info:
        ra = ltc.ReclassifyAbove(
            dtm,
            9,
            1,
            25.0
        )