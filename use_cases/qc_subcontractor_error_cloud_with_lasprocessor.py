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
from lastricks.core.lasprocessor import LASProcessor

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

def custom_kernel_func(path, main_input, *other_inputs):
    las = main_input.query_las(path)
    gt_las = other_inputs[0].query_las(path)
    return error_cloud(las, gt_las)

processor = LASProcessor(
    input_path,
    gt_input_path,
    kernel_func=custom_kernel_func,
    output_folder = output_path,
    rejected_folder = rejected_path
)
processor.run()
