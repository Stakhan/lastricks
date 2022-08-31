"""
The aim here is to generate an error cloud based on
        - the manual classification provided by a subcontractor
        - the final classification after QC
The action is performed on an 100 km² area split in 100 files.
"""
import sys
import time
from pathlib import Path
from datetime import timedelta

#sys.path.append('..')
from lastricks.qc import ErrorCloud
from lastricks.core import InputManager

root_path = Path(r"C:\Users\EAL\OneDrive - ESRI BELUX NV\Documents\R&D\repositories\lastricks\tmp")
input_path = root_path / "dir1"
gt_input_path = root_path / "dir2"
output_path = root_path / "out"

main_input = InputManager( input_path )
gt_input = InputManager( gt_input_path )

error_cloud = ErrorCloud(
    error_label = 1,
    correct_label = 0
)

for i, path in enumerate(main_input):
            startt = time.time()

            print(f"[{i+1}/{len(main_input)}]")
            
            las = main_input.query_las(path)
            gt_las = gt_input.query_las(path)

            las = error_cloud(las, gt_las)

            outlas_path = output_path / (path.stem+path.suffix)
            print(f"Writting to {outlas_path}")
            las.write( outlas_path )

            print(f"-- Processing time: {timedelta(seconds=time.time()-startt)}")