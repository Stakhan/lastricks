import pytest
import numpy as np
from laspy import ExtraBytesParams
from numpy.random import random_sample, randint
from ..lasdata_generator import generate_LasData

@pytest.fixture
def las6():
   """LAS representation with extra fields:
         - intensity (uint16)
         - classification (uint8)
         - scan_direction_flag (bool)
         - gps_time (float64)
         - intensity_float (float16)
         - error_mask (bool as uint8)
         - error_mask_float (bool as float16)
      Meant to test the CopyField LASProcess
   """
   las6 = generate_LasData(length=11)
   las6.add_extra_dims([
      ExtraBytesParams(
         name='intensity_float',
         type=np.float32,
         ),
      ExtraBytesParams(
         name='error_mask',
         type=np.uint8,
         ),
      ExtraBytesParams(
         name='error_mask_float',
         type=np.float32,
         ),
   ])
   las6.classification = [1,2,3,4,5,6,9,17,64,65,66]
   las6.intensity = random_sample(size=(11,)).astype('uint16')*100
   las6.intensity_float = random_sample(size=(11,)).astype('float16')*100
   las6.scan_direction_flag = randint(0, high=1, size=(11,)).astype('bool')
   las6.gps_time = random_sample(size=(11,)).astype('float64')*1e6
   las6.error_mask = randint(0, high=1, size=(11,)).astype('uint8')
   
   yield las6