import laspy
import fiona
import numpy as np
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


class DeliveryComparator:
    def __init__(
            self,
            delivery_1_path,
            delivery_2_path,
            vect_ref_path,
            output_path,
            crs = 'EPSG:2154'
        ):
        self.timer = Timer()
        self.main_input = InputManager(delivery_1_path)
        self.secondary_input = InputManager(delivery_2_path)
        self.output_path = output_path
        self.crs = crs
        output_path.mkdir(exist_ok=True)

        # Loading vector data used as reference (possibly in many layers)
        layers = fiona.listlayers(vect_ref_path) 
        refs = [
            gpd.read_file(vect_ref_path,
                          layer=layer,
                          crs=crs).geometry
            for layer in layers if layer != 'Default'
            ]
        self.ref = pd.concat(refs)

        self.stats = {
            'index': [],
            'nb_changes': [],
            'nb_expected_changes': [],
            'coverage_expected_changes_%': [],
            'nb_missing_changes': []
        }

    def generate_vector(self, las):
        self.log("Computing mask")
        mask = las.error_mask == 1
        x, y = las.x[mask], las.y[mask]
        self.log("Extracting points")
        points = [ Point(x[i], y[i]) for i in range(sum(mask)) ]
        ds = gpd.GeoSeries(
            points,
            crs=self.crs
            )
        self.log("Computing buffer")
        buffers = ds.buffer(1, resolution=6)
        self.log("Simplifying buffer")
        buffers_simplified = buffers.unary_union
        self.log("Explode MultiPolygon to Polygons")
        final_gs = gpd.GeoSeries([
            buffers_simplified
        ]).explode(index_parts=True)
    
        return final_gs
    
    def get_local_ref(self, tile_name):
        try:
            xmin, ymax = [int(v) for v in tile_name.split('_')]
        except Exception:
            raise ValueError(
                f"{tile_name} is not a valid name to proceed. "
                "Must be of form '<xmin>_<ymax>'."
            )
        xmax = xmin + 1000
        ymin = ymax - 1000
        return self.ref.cx[xmin:xmax, ymin:ymax]

    def intersection_mask(self, local_ref, cc_vect):
        """Returns a mask which is `True` when the
           reference vector matches with a change.

        Args:
            local_ref (geopandas.GeoSeries): local references
            cc_vect (geopandas.GeoSeries): change cloud as vector
        """
        inter_mask = []
        for ref_geom in local_ref:
            inter_mask.append(
            any( cc_vect.apply(ref_geom.intersects) )
            )
        return inter_mask
    
    def compute_stats(
        self,
        tile_name,
        cc_vect,
        ):
        local_ref = self.get_local_ref(tile_name)
        nb_inter = sum(
                self.intersection_mask(local_ref, cc_vect)
            )
        self.stats['index'].append( tile_name )
        self.stats['nb_changes'].append( len(cc_vect) )
        self.stats['nb_expected_changes'].append( len(local_ref) )
        self.stats['coverage_expected_changes_%'].append( nb_inter / len(local_ref) * 100 if len(local_ref) > 0 else 100 )
        self.stats['nb_missing_changes'].append( len(local_ref) - nb_inter )

    def produce_report(self):
        report_out = self.output_path / 'comparison_report'
        report_out.mkdir(exist_ok=True)

        # Stats per file
        stats_df = pd.DataFrame( data=self.stats )
        stats_df.to_csv(report_out / 'stats_per_file.csv', mode='a')

        # Summary
        stats_summary = {
            'index': ['TOTAL'],
            'nb_changes': [sum(self.stats['nb_changes'])],
            'nb_expected_changes': [sum(self.stats['nb_expected_changes'])],
            'coverage_expected_changes_%': [np.mean(self.stats['coverage_expected_changes_%'])],
            'nb_missing_changes':[sum(self.stats['nb_missing_changes'])]
        }
        stats_sum_df = pd.DataFrame( data=stats_summary )
        stats_sum_df.to_csv(report_out / 'stats_summary.csv', mode='a')

    def compare(self):
        for path in self.main_input:
            if not (output_path / f'change_map_{path.stem}.shp').exists():
                try:
                    self.log(f"Reading {path}")
                    las = self.main_input.query_las(path)
                    gt_las = self.secondary_input.query_las(path)
                    
                    self.log("Computing change cloud...")
                    cc_las = change_cloud(las, gt_las)
                    cc_vect = self.generate_vector(cc_las)
                    
                    self.log("Computing stats...")
                    self.compute_stats(path.stem, cc_vect)

                    self.log("Writing to SHP")
                    cc_vect.to_file(
                        output_path / f'change_map_{path.stem}.shp',
                        crs=self.crs
                    )
                    
                    self.log("Producing report")
                    self.produce_report()

                    self.log("Done")
                except Exception as e:
                    if True:
                        print(f"{e.__class__.__name__} when trying to process {path.name}")
                        continue
                    else:
                        raise e
            else:
                self.log(f"Skipping {path.stem}...")

    def log(self, msg):
        print(str(self.timer)+" | "+msg)

if __name__ == '__main__':


    root = Path("/mnt/share/00 Lidar - AI/Input data/12_Subcontractor_AREA1_PK")
    delivery_1_path = root / '03_Back2020909'
    delivery_2_path = root / '04_Back20220928' / 'laz'
    vect_ref_path = root / '03_Back2020909' / 'raport' / 'FR_038_3_Block_PK_AREA1_Naskatech_20220922.gpkg'
    output_path = Path(__file__).parent / 'output'
    crs = 'EPSG:2154'

    delivery_comparator = DeliveryComparator(
        delivery_1_path,
        delivery_2_path,
        vect_ref_path,
        output_path,
        crs = crs
    )
    delivery_comparator.compare()
