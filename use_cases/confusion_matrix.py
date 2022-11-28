import numpy as np
from pathlib import Path
from datetime import datetime
from lastricks.core import InputManager
from lastricks.core.utils import Timer
from sklearn.metrics import confusion_matrix

map_cls_to_names = { 1 : 'Unclassified',
                     2 : 'Ground',
                     3 : 'Vegetation',
                     4 : 'Vegetation',
                     6 : 'Building',
                     9 : 'Water',
                     14: 'Wire - Conductor',
                     17: 'Bridge',
                     64: 'Durable Overground',
                     65: 'Artifact',
                     66: 'Virtual Points' }

# class Timer:
#     def __init__(self):
#         self.start_time = datetime.now()
#     def __str__(self):
#         return str(datetime.now()-self.start_time)

timer = Timer()
def log(msg):
        print(str(timer)+" | "+msg)

if __name__ == '__main__':

    input_dl = InputManager(r"X:\00 Lidar - AI\Result\01_FR_LiDAR_HD\01_production\01_BlockPP_10p_ai\ai_pred_run4")
    input_tscan = InputManager(r"X:\00 Lidar - AI\Input data\14_BlocPP_10p\TerraScanAuto10%")
    output_path = Path(r"X:\00 Lidar - AI\Result\01_FR_LiDAR_HD\01_production\01_BlockPP_10p_ai\comp_tscan\run4_vs_tscan")

    cms = {}
    for path in input_tscan:
        if not (output_path / 'per_tile' / f'cm_{path.stem}.npy').exists():
            cx, cy = path.stem.split('_')
            log(f"Reading {path.stem}...")
            tscan = input_tscan.query_las(path)
            log(f'Semis_2021_{int(float(cx)/1e3):04d}_{int(float(cy)/1e3):04d}_LA93_IGN69_pred.laz')
            dl = input_dl.query_las(input_dl.input_path / f'Semis_2021_{int(float(cx)/1e3):04d}_{int(float(cy)/1e3):04d}_LA93_IGN69_pred.laz')

            classes = np.concat( 
                (np.unique(dl.classification),
                np.unique(tscan.classification))
                )
            labels = [map_cls_to_names[c] for c in classes]
            log(f"Computing confusion matrix...")
            cm = confusion_matrix(tscan.classification, dl.classification, labels=labels)
            cms[path] = cm
            (output_path / 'per_tile').mkdir(exist_ok=True)
            np.save(
                output_path / 'per_tile' / f'cm_{path.stem}.npy',
                cm
            )
            log("Done")