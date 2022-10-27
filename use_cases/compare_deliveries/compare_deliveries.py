import laspy
import fiona
import pandas as pd
import geopandas as gpd
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from shapely.geometry import Point

from lastricks.qc import ErrorCloud
from lastricks.core import InputManager

change_cloud = ErrorCloud(
    error_label = 1,
    correct_label = 0,
    map_awaited={
            0: 0,
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
            9: 9,
            17: 17,
            64: 64,
            65: 65
        }
)

class Timer:
    def __init__(self):
        self.start_time = datetime.now()
    def __str__(self):
        return str(datetime.now()-self.start_time)

def generate_vector(las, timer, crs='EPSG:2154'):

    print(f"{timer} | Computing mask for {path.stem}")
    mask = las.error_mask == 1
    x, y = las.x[mask], las.y[mask]
    print(f"{timer} | Extracting points from {path.stem}")
    points = [ Point(x[i], y[i]) for i in range(sum(mask)) ]
    ds = gpd.GeoSeries(
        points,
        crs=crs
        )
    print(f"{timer} | Computing buffer")
    buffers = ds.buffer(1, resolution=6)
    print(f"{timer} | Simplifying buffer")
    buffers_simplified = buffers.unary_union
    print(f"{timer} | Explode MultiPolygon to Polygons")
    final_gs = gpd.GeoSeries([
        buffers_simplified
    ]).explode(index_parts=True)
    
    return final_gs, timer

class DeliveryComparator:
    def __init__(
            self,
            delivery_1_path,
            delivery_2_path,
            vector_reference_path,
            output_path,
            crs = 'EPSG:2154'
        ):
        self.main_input = InputManager(delivery_1_path)
        self.secondary_input = InputManager(delivery_2_path)

if __name__ == '__main__':
    timer = Timer()

    root = Path(__file__).resolve().parents[2] / 'tmp' / 'compare_deliveries'
    
    main_input_path = root / 'delivery_1' / 'laz' / '921000_6541000.laz'
    secondary_input_path = root / 'delivery_2' / 'laz' / '921000_6541000.laz'
    vector_reference_path = root / 'delivery_1' / 'report' / 'FR_038_3_Block_PK_AREA1_Naskatech_20220922.gpkg'
    output_path = root / 'output'
    crs = 'EPSG:2154'
    
    output_path.mkdir(exist_ok=True)

    main_input = InputManager(main_input_path)
    secondary_input = InputManager(secondary_input_path)
    
    

    for path in main_input:
        print(f"{timer} | Reading {path}")
        las = main_input.query_las(path)
        gt_las = secondary_input.query_las(path)
        print(f"{timer} | Computing change cloud...")
        cc_las = change_cloud(las, gt_las)
        vector_data, timer = generate_vector(cc_las, timer)
        print(f"{timer} | Writing to SHP")
        vector_data.to_file(
            output_path / f'change_map_{path.stem}.shp',
            crs=crs
        )
        print(f"{timer} | Done")
    
    ## TODO
    ## Generate statistics on the fly
    # For each file (1km*1km tile):
    # + the number of changes in that file
    # + percentage of highlighted errors intersecting with changes