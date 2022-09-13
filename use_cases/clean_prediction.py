"""
Goal: clean water classifier (binary) prediction by removing points outside water database over the netherlands
"""

from pathlib import Path
import sys
sys.path.append('..')
from lastricks.cleaning import new_class_from_gpkg
import time
from datetime import timedelta

start_time = time.time()

gpkg_path = Path('data/top10nl_water_db_buffered_v2.gpkg')

lases_path = Path('/home/eal/Documents/tp3d/torch-points3d-eurosense/data/ahn4clust-dsb1-wc/predicted/pred_100sqkm_sample_zone_N654')

new_class_from_gpkg(
    gpkg_path,
    lases_path,
    9,
    1,
    output_folder=Path('/home/eal/Documents/tp3d/torch-points3d-eurosense/data/ahn4clust-dsb1-wc/predicted/pred_100sqkm_sample_zone_N654_cleaned_v2'),
    output_suffix='_cleaned',
    gpkg_as_mask=False
    )

print(f"----- Execution time: {timedelta(seconds=time.time()-start_time)}")
