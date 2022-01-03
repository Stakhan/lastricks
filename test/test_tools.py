import unittest
import laspy
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, Point

class Testhelpers(unittest.TestCase):

    def setUp(self):
        header = laspy.header.Header()
        mock_las = laspy.file.File("mock.las", mode="w", header=header)
        mock_las.X = [1000, 2000, 3000, 5000, 6000]
        mock_las.Y = [1000, 0, 0, 2000, 2000]
        mock_las.Z = [10.0, 10.0, 11.0, 9.0, 12.0]
        mock_las.classification = [1, 1, 2, 2, 1]
        mock_las.close()

        df = gpd.GeoDataFrame(geometry=[ Polygon([(0.5, 0.5), (0, 2), (2, 1)]) ])
        df.to_file("mock.gpkg", driver="GPKG")
    
    def test_setUp(self):
        lasfile = laspy.file.File("mock.las")
        d = gpd.read_file("mock.gpkg")
        p =  Point(lasfile.x[0], lasfile.y[0])
        self.assertEqual(len(d.geometry.apply(p.within).index), 1)

    def test_new_class_from_gpkg(self):
        pass

#    def tearDown(self):
#        (Path.cwd() / "mock.las").unlink()
#        (Path.cwd() / "mock.gpkg").unlink()

if __name__ == "__main__":
    unittest.main()
