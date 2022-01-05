import sys
import laspy
import unittest
import numpy as np
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, Point

sys.path.append('..')
import lastricks.tools as ltt


class Testhelpers(unittest.TestCase):

    def setUp(self):
    #     header = laspy.header.Header(scale=[0.1, 0.001, 0.001])
    #     mock_las = laspy.file.File("mock.las", mode="w", header=header)
    #     mock_las.X = np.array([1000, 2000, 3000000, 5000000, 6000000])
    #     mock_las.Y = np.array([1000, 0, 0, 2000000, 2000000])
    #     mock_las.Z = np.array([10.0, 10.0, 11.0, 9.0, 12.0])
    #     mock_las.classification = [1, 1, 2, 2, 1]
    #     mock_las.close()

        df = gpd.GeoDataFrame(geometry=[ Polygon([(0.5, 0.5), (0, 2), (2, 1)]) ])
        df.to_file("mock.gpkg", driver="GPKG")
    
    def test_setUp(self):
        lasfile = laspy.file.File("mock2.las")
        d = gpd.read_file("mock.gpkg")
        p =  Point(lasfile.x[0], lasfile.y[0])
        self.assertEqual(len(d.geometry.apply(p.within).index), 1)

    def test_new_class_from_gpkg(self):
        ltt.new_class_from_gpkg(
            "mock.gpkg",
            "mock2.las",
            1,
            8,
            output_folder=Path.cwd(),
            output_suffix="_wec",
            )
        res_lasfile = laspy.file.File(Path.cwd()/"mock2_wec.las", mode="r")
        self.assertEqual(res_lasfile.classification[0], 8)


if __name__ == "__main__":
    unittest.main()