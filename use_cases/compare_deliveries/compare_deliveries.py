import laspy
import fiona
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from shapely.geometry import Point, Polygon

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
        (output_path / 'missing_changes').mkdir(exist_ok=True)

        # Loading vector data used as reference (possibly in many layers)
        layers = fiona.listlayers(vect_ref_path) 
        refs = []
        for layer in layers:
            if layer != 'Default':
                ref_df = gpd.read_file(vect_ref_path, layer=layer, crs='EPSG:2154')
                ref_df['error_type'] = layer
                refs.append( ref_df )
        self.ref = pd.concat(refs)

        self.stats = {
            'index': [],
            'nb_changes': [],
            'nb_expected_changes': [],
            'nb_expected_changes_covered': [],
            'nb_expected_changes_missing': [],
            'coverage_expected_changes_%': [],
            'nb_pts_delivery_1': [],
            'nb_pts_delivery_2': []
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
    
        final_gdf = gpd.GeoDataFrame(geometry=final_gs)
        final_gdf['error_type'] = 'Unknown'
        return final_gdf
    
    def get_bbox(self, tile_name, tile_size=1000):
        try:
            xmin, ymax = [int(v) for v in tile_name.split('_')]
        except Exception:
            raise ValueError(
                f"{tile_name} is not a valid name to proceed. "
                "Must be of form '<xmin>_<ymax>'."
            )
        xmax = xmin + tile_size
        ymin = ymax - tile_size
        return xmin, xmax, ymin, ymax
    
    def get_bbox_polyg(self, tile_name):
        xmin, xmax, ymin, ymax = self.get_bbox(tile_name)
        bbox_polyg = Polygon([
            Point(xmin,ymin),
            Point(xmin,ymax),
            Point(xmax,ymax),
            Point(xmax,ymin),
            Point(xmin,ymin)
        ])
        return bbox_polyg

    def get_local_ref(self, tile_name):
        xmin, xmax, ymin, ymax = self.get_bbox(tile_name)
        return self.ref.cx[xmin:xmax, ymin:ymax]

    def intersection_masks(self, local_ref, cc_vect):
        """Returns a list of interesection masks between
           each reference geometry and all the changes.

        Args:
            local_ref (geopandas.GeoSeries): local references
            cc_vect (geopandas.GeoSeries): change vector map (geometries only)
        """
        inter_masks = []
        for ref_geom in local_ref:
            inter_masks.append(
                cc_vect.apply(ref_geom.intersects)
            )
        return inter_masks
    

    def compute_stats(
        self,
        tile_name,
        cc_vect,
        ):
        """Compute intersection statistics

        Args:
            tile_name (str): name of the tile for which the statistics
                are computed
            cc_vect (geopandas.GeoDataFrame): change vector map
        """
        local_ref = self.get_local_ref(tile_name)
        error_types = local_ref['error_type'].unique().tolist()
        missing_changes = []
        all_i_masks = []
        local_inter = []
        for et in error_types:
            et_mask = local_ref['error_type'] == et
            # Extracting intersection masks
            i_masks = self.intersection_masks(
                local_ref.geometry[et_mask],
                cc_vect.geometry
                )
            # Recording missing change
            missing_mask = [not any(mask) for mask in i_masks]
            missing_changes.append( local_ref.loc[missing_mask,et_mask] )
            # Recording error type
            cc_vect.loc[sum(i_masks).astype(bool),'error_type'] = et
            local_inter.append(np.sum(i_masks)>0)
        
        nb_inter = sum( local_inter )

        self.stats['index'].append( tile_name )
        self.stats['nb_changes'].append( len(cc_vect) )
        self.stats['nb_expected_changes'].append( len(local_ref) )
        self.stats['coverage_expected_changes_%'].append( nb_inter / len(local_ref) * 100 if len(local_ref) > 0 else 100 )
        self.stats['nb_expected_changes_covered'].append( nb_inter )
        self.stats['nb_expected_changes_missing'].append( len(local_ref) - nb_inter )

        if len(missing_changes) > 0:
            return cc_vect, pd.concat(missing_changes)
        else:
            return cc_vect, missing_changes
    
    def set_stats_mismatch(self, tile_name):
        self.stats['index'].append( tile_name )
        self.stats['nb_changes'].append( 0 )
        self.stats['nb_expected_changes'].append( 0 )
        self.stats['coverage_expected_changes_%'].append( 0 )
        self.stats['nb_expected_changes_missing'].append( 0 )
        self.stats['nb_expected_changes_covered'].append( 0 )

    def record_file_size(self, las_d1, las_d2):
        self.stats['nb_pts_delivery_1'].append( len(las_d1) )
        self.stats['nb_pts_delivery_2'].append( len(las_d2) )

    def produce_report(self):
        report_out = self.output_path / 'comparison_report'
        report_out.mkdir(exist_ok=True)

        # Stats per file
        stats_df = pd.DataFrame( data=self.stats )
        stats_df.to_csv(report_out / 'stats_per_file.csv', sep=';', mode='w')

        # Stats summary
        stats_summary = {
            'index': ['TOTAL'],
            'nb_changes': [sum(self.stats['nb_changes'])],
            'nb_expected_changes': [sum(self.stats['nb_expected_changes'])],
            'coverage_expected_changes_%': [np.mean(self.stats['coverage_expected_changes_%'])],
            'nb_expected_changes_missing':[sum(self.stats['nb_expected_changes_missing'])],
            'nb_expected_changes_covered':[sum(self.stats['nb_expected_changes_covered'])],
        }
        stats_sum_df = pd.DataFrame( data=stats_summary )
        stats_sum_df.to_csv(report_out / 'stats_summary.csv', sep=';', mode='w')

    def compare(self):
        for path in self.main_input:
            if not (self.output_path / f'change_map_{path.stem}.shp').exists():
                try:
                    self.log(f"Reading {path}")
                    las_d1 = self.main_input.query_las(path)
                    las_d2 = self.secondary_input.query_las(path)
                    
                    if len(las_d1) != len(las_d2):
                        bbox_polyg = self.get_bbox_polyg(path.stem)
                        cc_vect = gpd.GeoDataFrame(geometry=[bbox_polyg], crs=self.crs)
                        cc_vect['error_type'] = 'nb_points_mismatch'
                        self.set_stats_mismatch(path.stem)
                    else:
                        self.log("Computing change cloud...")
                        cc_las = change_cloud(las_d1, las_d2)
                        cc_vect = self.generate_vector(cc_las)
                    
                        self.log("Computing stats...")
                        cc_vect, missing_changes = self.compute_stats(path.stem, cc_vect)
                        
                        self.log("Writing missing changes to SHP")
                        if len(missing_changes) > 0:
                            missing_changes.to_file(
                                self.output_path / 'missing_changes' / f'missing_changes_{path.stem}.shp',
                                crs=self.crs
                            )

                    self.record_file_size(las_d1, las_d2)

                    self.log("Writing changes to SHP")
                    cc_vect.to_file(
                        self.output_path / f'change_map_{path.stem}.shp',
                        crs=self.crs
                    )
                    
                    
                    self.log("Producing report")
                    self.produce_report()

                    self.log("Done")
                except Exception as e:
                    if False:
                        print(f"{e.__class__.__name__} when trying to process {path.name}")
                        continue
                    else:
                        raise e
            else:
                self.log(f"Skipping {path.stem}...")

    def log(self, msg):
        print(str(self.timer)+" | "+msg)

if __name__ == '__main__':


    # root = Path("/mnt/share/00 Lidar - AI/Input data/12_Subcontractor_AREA1_PK")
    # delivery_1_path = root / '03_Back2020909'
    # delivery_2_path = root / '04_Back20220928' / 'laz'
    # vect_ref_path = root / '03_Back2020909' / 'raport' / 'FR_038_3_Block_PK_AREA1_Naskatech_20220922.gpkg'
    
    root = Path(r"X:\00 Lidar - AI\Input data\999_TESTING\03_compare_deliveries")
    delivery_1_path = root / 'delivery_1' / 'laz'
    delivery_2_path = root / 'delivery_2' / 'laz'
    vect_ref_path = root / 'delivery_1' / 'report' / 'FR_038_3_Block_PK_AREA1_Naskatech_20220922.gpkg'
    output_path = root / 'output'
    
    crs = 'EPSG:2154'

    delivery_comparator = DeliveryComparator(
        delivery_1_path,
        delivery_2_path,
        vect_ref_path,
        output_path,
        crs = crs
    )

    delivery_comparator.compare()
