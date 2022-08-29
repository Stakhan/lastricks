import laspy
import pytest
import numpy as np
from pathlib import Path
from numpy.random import random_sample, randint

def generate_LasData():
    "Generates a random LAS/LAZ representaiton."

    allX, allY, allZ = ( random_sample(size=(10,))*100,
                         random_sample(size=(10,))*100,
                         random_sample(size=(10,))*100 )

    Xmin, Ymin, Zmin = ( np.floor(np.min(allX)),
                         np.floor(np.min(allY)),
                         np.floor(np.min(allZ)) )

    Xmax, Ymax, Zmax = ( np.ceil(np.max(allX)),
                         np.ceil(np.max(allY)),
                         np.ceil(np.max(allZ)) )

    mock_hdr = laspy.LasHeader(version="1.4", point_format=1)
    mock_hdr.offsets, mock_hdr.scales = [0.0,0.0,0.0],[0.001,0.001,0.001]
    mock_hdr.mins, mock_hdr.maxs = [Xmax,Ymax,Zmax], [Xmax,Ymax,Zmax]

    mock_las = laspy.LasData(mock_hdr)
    mock_las.X, mock_las.Y, mock_las.Z = allX, allY, allZ

    return mock_las

@pytest.fixture
def las_classif_to_compare(tmp_path):
    las1 = generate_LasData()
    las2 = generate_LasData()

    las1.classification = [1,1,2,2,3,3,4,4,5,5]
    las2.classification = [2,2,1,1,3,3,4,4,5,5]

    yield las1, las2
