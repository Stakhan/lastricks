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

lases_path = Path(r'/mnt/share/00 Lidar - AI/Input data/10_N675_AHN4_2022/00_ZONE1/zone1A/prediction_output_zone1A')

new_class_from_gpkg(
    gpkg_path,
    lases_path,
    9,
    1,
    output_folder=Path(r'/mnt/share/00 Lidar - AI/Input data/10_N675_AHN4_2022/00_ZONE1/zone1A/prediction_output_zone1A_cleaned1'),
    output_suffix='_c1',
    gpkg_as_mask=False
    )

print(f"----- Execution time: {timedelta(seconds=time.time()-start_time)}")
