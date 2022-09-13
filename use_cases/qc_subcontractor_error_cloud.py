"""
The aim here is to generate an error cloud based on
        - the manual classification provided by a subcontractor
        - the final classification after QC
The action is performed on a 172 km² area split in 172 files.
"""
import sys
import time
import shutil
import numpy as np
from pathlib import Path
from datetime import timedelta

from lastricks.qc import ErrorCloud
from lastricks.core import InputManager

root_path = Path("/home/eal/Downloads/07_BlockPK_SubcontractorTest")
input_path = root_path / "00_subcontractor_work"
gt_input_path = root_path / "01_delivered"
output_path = root_path / "02_error_cloud"
rejected_path = root_path / "03_rejected"

main_input = InputManager( input_path )
gt_input = InputManager( gt_input_path )

error_cloud = ErrorCloud(
    error_label = 1,
    correct_label = 0
)

for i, path in enumerate(main_input):
    outlas_path = output_path / (path.stem+path.suffix)
    if not outlas_path.exists():
        startt = time.time()

        print(f"[{i+1}/{len(main_input)}] Processing {path.stem}...")
        
        las = main_input.query_las(path)
        gt_las = gt_input.query_las(path)

        try:
            las = error_cloud(las, gt_las)
        except Exception as e:
            las_classif = np.array(las.classification)
            las_ref_classif = np.array(gt_las.classification)
            print('sizes', len(las_classif), len(las_ref_classif))
            print(
                'unique values',
                np.unique(las_classif, return_counts=True),
                np.unique(las_ref_classif, return_counts=True)
                )
            shutil.move(
                path,
                rejected_path / path.name
            )
            print(f"Error {e} occured. {path.stem} got "
                f"moved to '{rejected_path.name}'")
            continue

        print(f"Writting to {outlas_path}")
        las.write( outlas_path )

        print(f"-- Processing time: {timedelta(seconds=time.time()-startt)}")
