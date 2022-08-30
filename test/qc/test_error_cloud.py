import sys
import pytest
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks.qc as ltqc

def test_error_cloud(las_classif_to_compare):
    las1, las2 = las_classif_to_compare
    
    ec = ltqc.ErrorCloud(
        error_label=1,
        correct_label=0
    )

    las_ec = ec(las1, las2)

    assert las_ec.error_mask.tolist() == [1,1,1,1,0,0,0,0,0,0]