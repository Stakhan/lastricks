import laspy
import numpy as np
import pandas as pd
from shapely.geometry import Polygon

def read_mins_maxs(
    input_file,
    from_filename=False,
    tile_size=(1000,1250)
    ):
    if from_filename:
        try:
            parts = input_file.name.split('_')
            parts = [int(p) for p in parts[:2]]
        except:
            ValueError(
                "Filename should be in the form 'coordX_coordY*'"
                f" but got {input_file.name}"
            )
        else:
            mins = [ parts[0]             , parts[1]              ]
            maxs = [ parts[0]+tile_size[0], parts[1]+tile_size[1] ]
            return mins, maxs
    else:
        with laspy.open(input_file) as f:
            return f.header.mins, f.header.maxs

def bbox(input_path, from_filename=False):
    if input_path.is_file():
        mins, maxs = read_mins_maxs(input_path, from_filename=from_filename)
    elif input_path.is_dir():
        indexes = [p.name for p in input_path.iterdir() if p.suffix in ['.las', '.laz']]
        nb_tiles = len(indexes)
        df = pd.DataFrame(
            index=indexes,
            columns=['minX', 'minY', 'maxX', 'maxY'])
        for path in input_path.iterdir():
            if path.suffix in ['.las', '.laz']:
                tmpmins, tmpmaxs = read_mins_maxs(path, from_filename=from_filename)
                df.at[path.name,'minX'] = tmpmins[0]
                df.at[path.name,'minY'] = tmpmins[1]
                df.at[path.name,'maxX'] = tmpmaxs[0]
                df.at[path.name,'maxY'] = tmpmaxs[1]
                
        mins = [df['minX'].min(), df['minY'].min()]
        maxs = [df['maxX'].max(), df['maxY'].max()]
    return Polygon([
            (mins[0], mins[1]),
            (maxs[0], mins[1]),
            (maxs[0], maxs[1]),
            (mins[0], maxs[1]),
            (mins[0], mins[1])
        ])