import laspy
import geopandas as gpd
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from shapely.geometry import Point
from lastricks.core import InputManager

class Timer:
    def __init__(self):
        self.start_time = datetime.now()
    def __str__(self):
        return str(datetime.now()-self.start_time)

if __name__ == '__main__':
    timer = Timer()
    input_ec_path = Path(__file__).parents[1] / 'tmp' / 'out'
    input_ec = InputManager(input_ec_path)
    output_vect_path = input_ec_path.parent / 'out_vect'
    output_vect_path.mkdir(exist_ok=True)

    for path in input_ec:
        print(f"{timer} | Reading {path}")
        las = input_ec.query_las(path)
        print(f"{timer} | Computing mask for {path.stem}")
        mask = las.error_mask == 1
        x, y = las.x[mask], las.y[mask]
        print(f"{timer} | Extracting points from {path.stem}")
        points = [Point(x[i], y[i]) for i in range(sum(mask))]
        ds = gpd.GeoSeries(
            points,
            crs='EPSG:2154'
            )
        print(f"{timer} | Computing buffer")
        buffers = ds.buffer(1, resolution=6)
        print(f"{timer} | Simplifying buffer")
        buffers_simplified = buffers.unary_union
        print(f"{timer} | Explode MultiPolygon to Polygons")
        final_gs = gpd.GeoSeries([
            buffers_simplified
        ]).explode(index_parts=True)
        print(f"{timer} | Writing to GPKG")
        final_gs.to_file(
        output_vect_path / f'change_map_{path.stem}.shp'
        )
        print(f"{timer} | Done")