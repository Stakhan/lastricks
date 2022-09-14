import sys
import pytest
import numpy as np
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks.las2las as l2l

def test_copy_field(las6):    
    cf = l2l.CopyField('classification', 'intensity')
    assert las6.classification.tolist() != las6.intensity.tolist()
    las_cf = cf(las6)
    assert las_cf.intensity.tolist() == las_cf.classification.tolist()

def test_copy_field_conversion(las6):
    # int to...
    # float
    cf = l2l.CopyField('classification', 'gps_time')
    assert las6.classification.tolist() == cf(las6).gps_time.tolist()
    # bool
    cf = l2l.CopyField('error_mask', 'scan_direction_flag')
    assert np.array(las6.error_mask).tolist() == np.array(cf(las6).scan_direction_flag).tolist()

    #float to...
    # int
    cf = l2l.CopyField('intensity_float', 'intensity')
    assert las6.intensity_float.astype('uint16').tolist() == cf(las6).intensity.tolist()
    # bool
    cf = l2l.CopyField('error_mask_float', 'scan_direction_flag')
    assert np.array(las6.error_mask_float).tolist() == np.array(cf(las6).scan_direction_flag).tolist()

    # bool to...
    # float
    cf = l2l.CopyField('scan_direction_flag', 'intensity_float')
    assert np.array(las6.scan_direction_flag).tolist() == np.array(cf(las6).intensity_float).tolist()
    # int
    cf = l2l.CopyField('scan_direction_flag', 'classification')
    assert np.array(las6.scan_direction_flag).tolist() == np.array(cf(las6).classification).tolist()

def test_copy_field_create_new_dim(las6):
    cf = l2l.CopyField('classification', 'classification_copy',  create_dim_if_needed=True)
    assert las6.classification.tolist() == cf(las6).classification_copy.tolist()