import numpy as np
import pandas as pd
from pathlib import Path

root = Path(r"/mnt/share/00 Lidar - AI/Result/01_FR_LiDAR_HD/01_production/01"
            r"_BlockPP_10p_ai/comp_tscan")
cm_run18_path = root / "run18_vs_tscan/per_tile"
output_path = Path(root / "run18_vs_tscan")

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

names = list(map_cls_to_names.values())
cls_id = list(map_cls_to_names.keys())
map_cls_to_range = {k:i for i,k in enumerate(cls_id)}

cmdf = pd.DataFrame(index=cls_id, columns=cls_id)
cmdf[:] = 0

for path in cm_run18_path.iterdir():
    print(f"Processing {path.stem}")
    cm = np.load(path)
    local_cls = [int(n) for n in path.stem.split('_')[-1].split('-')]
    for i_cm,i in enumerate(local_cls):
        for j_cm,j in enumerate(local_cls):
            cmdf.at[i,j] += cm[i_cm,j_cm]

    cmdf.to_excel(output_path / 'cm_total_run18.xlsx')
    print("Done")