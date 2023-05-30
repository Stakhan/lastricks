import numpy as np
from laspy import LasData

def concat_las(las1: LasData, las2: LasData):
    hdr1, hdr2 = las1.header, las2.header
    assert hdr1.point_format == hdr2.point_format
    assert hdr1.scales == hdr2.scales
    assert hdr1.offsets == hdr2.offsets
    lasconcat = LasData(las1.header)
    for dim in lasconcat.header.point_format.dimension_names:
        lasconcat[dim] = np.concatenate((las1[dim], las2[dim]))
    return lasconcat