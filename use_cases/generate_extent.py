import sys
import time
import laspy
import geopandas as gpd
from pathlib import Path
from datetime import timedelta

root = Path(__file__).resolve().parent

sys.path.insert(0, str(root.parent))
from lastricks.manylas import info

folder_of_laz = Path(r"/mnt/share/00 Lidar - AI/Input data/11_TESTING/simple_tiling_final")

polygons = []
names = []

for lasfile in folder_of_laz.iterdir():
    if lasfile.suffix == '.laz':
        polygons.append(
            info.bbox(lasfile)
        )
        names.append(lasfile.name)

d = gpd.GeoDataFrame(
    data={'names': names,
          'geometry': polygons},
    crs='EPSG:2154'
    )
output = root/'test_footprint.gpkg'
d.to_file(output, driver='GPKG')