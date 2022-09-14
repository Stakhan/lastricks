import laspy
import numpy as np
from numpy.random import random_sample

def generate_LasData(length=10):
    "Generates a random LAS/LAZ representation."

    allX, allY, allZ = ( random_sample(size=(length,))*100,
                         random_sample(size=(length,))*100,
                         random_sample(size=(length,))*100 )

    Xmin, Ymin, Zmin = ( np.floor(np.min(allX)),
                         np.floor(np.min(allY)),
                         np.floor(np.min(allZ)) )

    Xmax, Ymax, Zmax = ( np.ceil(np.max(allX)),
                         np.ceil(np.max(allY)),
                         np.ceil(np.max(allZ)) )

    mock_hdr = laspy.LasHeader(version="1.4", point_format=6)
    mock_hdr.offsets, mock_hdr.scales = [0.0,0.0,0.0],[0.001,0.001,0.001]
    mock_hdr.mins, mock_hdr.maxs = [Xmax,Ymax,Zmax], [Xmax,Ymax,Zmax]

    mock_las = laspy.LasData(mock_hdr)
    mock_las.X, mock_las.Y, mock_las.Z = allX, allY, allZ

    return mock_las