import sys
import time
from pathlib import Path
from datetime import timedelta

sys.path.append('..')
from lastricks.cleaning import Cleaner, ReclassifyAbove

cleaning_pipeline = [
    ReclassifyAbove(
        r"/mnt/share/00 Lidar - AI/Input data/10_N675_AHN4_2022/09_DTM20m_Netherlands/Netherlands_DTM_20m.tif",
        9,
        1,
        threshold
    )
]

cleaner = Cleaner()