import sys
import laspy
import unittest
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks as lt


class Testhelpers(unittest.TestCase):

    def setUp(self):
        header = laspy.header.Header(scale=[0.001, 0.001, 0.001])

        gt_las = laspy.file.File(root_path/"data"/"mock_gt.las", mode="w", header=header)
        gt_las.X = np.array([1000, 2000, 3000, 5000, 6000])
        gt_las.Y = np.array([1000, 2000, 3000, 5000, 6000])
        gt_las.Z = np.array([1000, 2000, 3000, 5000, 6000])
        gt_las.classification = [1, 9, 9, 9, 1]
        

        pred_las = laspy.file.File(root_path/"data"/"mock_pred.las", mode="w", header=header)
        pred_las.points = gt_las.points
        pred_las.classification =[1, 9, 9, 1, 1]

        filter_las = laspy.file.File(root_path/"data"/"mock_filter.las", mode="w", header=header)
        filter_las.points = gt_las.points
        filter_las.classification =[1, 9, 8, 8, 1]

        gt_las.close()
        pred_las.close()
        filter_las.close()

    def test_metrics_subcloud(self):
        expected_res = pandas.DataFrame(data={})
        res = lt.metrics_subcloud(root_path/"data"/"mock_gt.las", root_path/"data"/"mock_pred.las", root_path/"data"/"mock_filter.las", 8)
    