import sys
import time
from pathlib import Path
from datetime import timedelta

sys.path.insert(0, '..')
from lastricks.cleaning import Cleaner, ReclassifyAbove, NewClassFromGpkg
from lastricks.manylas.info import bbox

if __name__ == '__main__':

    input_path = Path(r"/mnt/share/00 Lidar - AI/Result/00_N675_AHN4_2022/03_Area9/Part1/prediction_m49")
    output_folder = Path(r"/mnt/share/00 Lidar - AI/Result/00_N675_AHN4_2022/03_Area9/Part1/prediction_m49_cleaned")
    output_suffix = "_c"
    output_format = "laz"

    assert input_path.exists()
    assert output_folder.exists()
    assert output_format in ['las', 'laz', '.las', '.laz'] 

    cleaning_pipeline = [
        NewClassFromGpkg(
            r'/home/eal/production_data/top10nl_water_db_buffered_v2.gpkg',
            9,
            1,
            gpkg_as_mask=False,
            bbox=bbox(input_path, from_filename=True)
        ),
        ReclassifyAbove(
            r"/home/eal/production_data/Netherlands_DTM_20m.tif",
            9,
            1,
            10
        )
    ]


    print('INPUT:', input_path)
    print('OUTPUT_FOLDER:', output_folder)

    cleaner = Cleaner(
        input_path,
        cleaning_pipeline,
        output_folder=output_folder,
        output_suffix=output_suffix,
        output_format=output_format
    )

    try:
        cleaner.clean()
    except BrokenPipeError:
        print("Catched BrokenPipeError and tried to finish gracefully")
    except Exception as e:
        print(f"Other Exception: {e}")