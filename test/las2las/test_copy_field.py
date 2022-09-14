import sys
import pytest
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks.las2las as l2l

def test_copy_field(las6):    
    cf = l2l.CopyField('classification', 'intensity')
    assert las6.classification.tolist() != las6.intensity.tolist()
    las_cf = cf(las6)
    assert las_cf.intensity.tolist() == las_cf.classification.tolist()
