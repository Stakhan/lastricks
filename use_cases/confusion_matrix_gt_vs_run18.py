import shutil
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from lastricks.core import InputManager
#from lastricks.core.utils import Timer
from sklearn.metrics import confusion_matrix

map_cls_to_names = { 0 : 'Never Classified',
                     1 : 'Unclassified',
                     2 : 'Ground',
                     3 : 'Low Vegetation',
                     4 : 'Medium Vegetation',
                     5 : 'High Vegetation',
                     6 : 'Building',
                     9 : 'Water',
                     14: 'Wire - Conductor',
                     17: 'Bridge',
                     64: 'Durable Overground',
                     65: 'Artifact',
                     66: 'Virtual Points' }
names = list(map_cls_to_names.values())
cls_id = list(map_cls_to_names.keys())

class Timer:
    def __init__(self):
        self.start_time = datetime.now()
    def __str__(self):
        return str(datetime.now()-self.start_time)

timer = Timer()
def log(msg):
        print(str(timer)+" | "+msg)

if __name__ == '__main__':

    input_gt = InputManager(r"/mnt/share/00 Lidar - AI/Input data/15_BlockPK_10p/03_final_delivery")
    input_tscan = InputManager(r"/mnt/share/00 Lidar - AI/Input data/15_BlockPK_10p/01_ai_run18")
    output_path = Path(r"/mnt/share/00 Lidar - AI/Result/01_FR_LiDAR_HD/01_production/02_BlockPK_10p_stats/gt_vs_run18")

    # Patterns
    # ai_run18: Semis_2021_0906_6534_LA93_IGN69_pred 
    # ground truth: Semis_2021_0906_6534_LA93_IGN69

    cms = {}
    cmdf = pd.DataFrame(index=cls_id, columns=cls_id)
    cmdf[:] = 0
    for path in input_tscan:
        if not len(
            list((output_path / 'per_tile').glob(f'cm_{path.stem}*.npy'))
            ) > 0:
            try:
                log(f"Reading {path.name}...")
                tscan = input_tscan.query_las(path)
                pattern_gt = ('_'.join(path.stem.split('_')[:-1])
                               + ".laz")
                print(f"Pattern gt: {pattern_gt}")
                dl_path = input_gt.input_path / pattern_gt
                log(f"Reading  {dl_path.name}...")
                dl = input_gt.query_las(dl_path)

                classes = np.unique(np.concatenate(
                    (np.array(tscan.classification),
                    np.array(dl.classification))
                ))
                print(classes)
                log(f"Computing confusion matrix...")
                cm = confusion_matrix(tscan.classification, dl.classification)
                for i_cm,i in enumerate(classes):
                    for j_cm,j in enumerate(classes):
                        cmdf.at[i,j] += cm[i_cm,j_cm]
                (output_path / 'per_tile').mkdir(exist_ok=True)
                np.save(
                    output_path / 'per_tile' / f'cm_{path.stem}_{"-".join([str(c) for c in classes])}.npy',
                    cm
                )
                cmdf.to_csv(output_path / 'cm_total.csv', sep=';', mode='w')
                log("Done")

            except Exception as e:
                if True:
                    print(f"{e.__class__.__name__} when trying to process {path.name}")
                    (input_tscan.input_path / 'rejected').mkdir(exist_ok=True)
                    shutil.move(
                        input_tscan.input_path / path.name,
                        input_tscan.input_path / 'rejected' / path.name
                    )
                    continue
                else:
                    raise e
        else:
            log(f"Skipping {path.name}...")
