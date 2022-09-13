from pathlib import Path
import sys
sys.path.append('..')
from lastricks.cleaning import new_class_from_gpkg
import time
from datetime import timedelta

start_time = time.time()

gpkg_path = Path('/home/eal/Documents/AHN4Sample_analysis/investigations/ditches_as_extra_class/data/top10nl_Waterdeel_ALL_polygon_v3.gpkg')

missing_ones = ["108000_421250.las", "110000_421250.las", "107000_430000.las", "107000_430000.las", "112000_427500.las", "110000_422500.las"]

root_path = Path('/home/eal/Documents/tp3d/torch-points3d-eurosense/data/ahn4clust-dod1-wc/raw/')

for path in [root_path/filename for filename in missing_ones]:
    if path.is_file() and path.suffix == '.las':
        print(f'Processing {path.name}')
        new_class_from_gpkg(
            gpkg_path,
            path,
            9,
            8,
            output_folder=Path('/home/eal/Documents/AHN4Sample_analysis/investigations/ditches_as_extra_class/data/ahn4clust-dec1-wc/raw')
            )

print(f"----- Execution time: {timedelta(seconds=time.time()-start_time)}")