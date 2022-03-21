import sys
import laspy
import pytest
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
from common_fixtures_v2 import mock_las_v2, folder_mock_las_v2
from lastricks.manylas import info

def test_read_mins_maxs(mock_las_v2):
    mins, maxs = info.read_mins_maxs(mock_las_v2)
    a = laspy.read(mock_las_v2)
    assert (mins[0], mins[1], maxs[0], maxs[1]) == (0.5 , 0., 6., 3.)

def test_bbox_folder(folder_mock_las_v2):
    polygon = info.bbox(folder_mock_las_v2)
    
    mins, maxs = [0.5 , 0.], [ 6., 3.]
    expected_polygon = Polygon([
        (mins[0], mins[1]),
        (maxs[0], mins[1]),
        (maxs[0], maxs[1]),
        (mins[0], maxs[1]),
        (mins[0], mins[1])
    ])
    assert polygon.equals(expected_polygon)


def test_bbox_file(mock_las_v2):
    polygon = info.bbox(mock_las_v2)
    
    mins, maxs = [0.5 , 0.], [ 6., 3.]
    expected_polygon = Polygon([
        (mins[0], mins[1]),
        (maxs[0], mins[1]),
        (maxs[0], maxs[1]),
        (mins[0], maxs[1]),
        (mins[0], mins[1])
    ])
    assert polygon.equals(expected_polygon)