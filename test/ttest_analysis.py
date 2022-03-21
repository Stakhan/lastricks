import sys
import laspy
import unittest
import numpy as np
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks as lt


class Testhelpers(unittest.TestCase):

    def setUp(self):
        header = laspy.LasHeader(version="1.4", point_format=1)
        header.scales = [0.001, 0.001, 0.001]
        
        gt_las = laspy.LasData(header)
        gt_las.X = np.array([1000, 2000, 3000, 5000, 6000])
        gt_las.Y = np.array([1000, 2000, 3000, 5000, 6000])
        gt_las.Z = np.array([1000, 2000, 3000, 5000, 6000])
        gt_las.classification = [1, 9, 9, 9, 1]
        out_path = root_path / "data" / "mock_gt.las"
        gt_las.write(out_path)

        pred_las = laspy.LasData(header)
        pred_las.points = gt_las.points
        pred_las.classification =[1, 9, 9, 1, 1]
        pred_las.write(root_path / "data" / "mock_pred.las")

        filter_las = laspy.LasData(header)
        filter_las.points = gt_las.points
        filter_las.classification =[1, 9, 8, 8, 1]
        filter_las.write(root_path/"data"/"mock_filter.las")

    def test_metrics_subcloud(self):
        expected_res = pandas.DataFrame(data={})
        res = lt.metrics_subcloud(root_path/"data"/"mock_gt.las", root_path/"data"/"mock_pred.las", root_path/"data"/"mock_filter.las", 8)
    