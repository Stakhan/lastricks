import laspy
import numpy as np
from shapely.geometry import Polygon

def read_mins_maxs(input_file):
    flas = open(input_file, 'rb')
    with laspy.open(flas, closefd=False) as f:
        return f.header.mins, f.header.maxs

def bbox(input_path):
    if input_path.is_file():
        mins, maxs = read_mins_maxs(input_path)
    elif input_path.is_dir():
        mins, maxs = [np.inf, np.inf], [np.inf, np.inf]
        for path in input_path.iterdir():
            if path.suffix in ['.las', '.laz']:
                tmpmins, tmpmaxs = read_mins_maxs(path)
                mins = [min(mins[i],tmpmins[i]) for i in range(2)]
                maxs = [min(maxs[i],tmpmaxs[i]) for i in range(2)]
    return Polygon([
            (mins[0], mins[1]),
            (maxs[0], mins[1]),
            (maxs[0], maxs[1]),
            (mins[0], maxs[1])
        ])