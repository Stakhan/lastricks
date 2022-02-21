"""
/!\\ These tests are meant to be used with laspy 2.x
"""
import sys
import laspy
import rasterio
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks.cleaning as ltc
from .common_fixtures_v2 import mock_las_v2, folder_mock_las_v2, mock_dtm
 

def test_reclassify_above(mock_las_v2, mock_dtm):
    ltc.reclassify_above(
        mock_dtm,
        mock_las_v2,
        9,
        1,
        25,
        output_folder=mock_las_v2.parent,
        output_suffix="_reclassified_above"
    )

    dtm = rasterio.open(mock_dtm)
    print(dtm.read(1))

    
    res_lasfile = laspy.read(mock_las_v2.parent / "mock_reclassified_above.las")
    assert res_lasfile.classification[1] == 9
    assert res_lasfile.classification[4] == 9