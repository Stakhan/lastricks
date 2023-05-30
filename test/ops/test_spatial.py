import sys
from pathlib import Path
from shapely.geometry import Point
root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
from lastricks.ops import spatial_query, get_bbox

from ..lasdata_generator import generate_LasData

def test_spatial_query():
    las = generate_LasData(length=3)
    query_geom = Point(las.x[0], las.y[0]).buffer(0.001)
    sub_las = spatial_query(las, query_geom)
    assert len(sub_las) == 1

def test_get_bbox(tmp_path):
    las = generate_LasData(length=3)
    las_path = tmp_path / 'test.las'
    las.write(las_path)
    bbox = get_bbox(las_path)
    points = [Point(las.x[i], las.y[i]) for i in range(len(las))]
    assert all( p.intersects(bbox) for p in points )