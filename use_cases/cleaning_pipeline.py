import sys
import time
import laspy
from pathlib import Path
from datetime import timedelta

sys.path.append('..')
from lastricks.cleaning import Cleaner, ReclassifyAbove
from lastricks.manylas import info

if __name__ == '__main__':
    cleaning_pipeline = [
        NewClassFromGpkg(
        r"/mnt/share/00 Lidar - AI/Input data/07_TOP10NL_WATER_DB/top10nl_water_db_buffered_v2.gpkg",
        9,
        1,
        gpkg_as_mask=False,
        bbox=info.bbox(input_path)
        ),
        ReclassifyAbove(
            r"/mnt/share/00 Lidar - AI/Input data/09_DTM20m_Netherlands/Netherlands_DTM_20m.tif",
            9,
            1,
            10
        )
    ]
    base_path = Path(r"/mnt/share/00 Lidar - AI/Result/00_N675_AHN4_2022/00_ZONE1/1A")
    input_path = base_path / "prediction_output_zone1A_cleaned1"
    output_folder = base_path / "prediction_output_zone1A_cleaned2"

    print('INPUT:', input_path)
    print('OUTPUT:', output_folder)

    cleaner = Cleaner(
        input_path,
        cleaning_pipeline,
        output_folder=output_folder,
        output_suffix='_c2'
    )

    cleaner.clean()