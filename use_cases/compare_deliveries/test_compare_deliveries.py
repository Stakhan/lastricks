import laspy
import pytest
import shapely.wkt
import numpy as np
import pandas as pd
import geopandas as gpd
from laspy import LasData
from math import floor, ceil
from compare_deliveries import DeliveryComparator

# Testing data
test_coords = {
    'las1': {
        'x':[
            928686.946673539,
            928843.010403544,
            929002.437576006,
            928820.138994836,
            928612.278250994,
            928935.168726866, 
        ],
        'y':[
            6547381.25004838,
            6547318.01733019,
            6547213.07792553,
            6547167.33510812,
            6547227.87707235,
            6547211.05986006,
        ]
    },
    'las2': {
        'x': [
            929045.489639455,
            928919.696891563,
            928630.440840262,
            928778.43230837,
        ],
        'y': [
            6547345.59755834,
            6547041.54236023,
            6547063.74108044,
            6547045.57849118,
        ]
    }
}

test_polygons_wkt = [
        "POLYGON ((928695.0189354363 6547375.195851962, 928719.2357211265 654"
        "7342.906804375, 928685.6012965566 6547317.344641702, 928654.65762595"
        "23 6547345.597558341, 928695.0189354363 6547375.195851962))",
        "POLYGON ((928822.8297488021 6547373.85047498, 928816.1028638881 6547"
        "388.64962179, 928830.9020106989 6547399.412637653, 928848.3919114753"
        " 6547399.412637653, 928864.5364352689 6547388.64962179, 928853.77341"
        "94065 6547363.087459117, 928832.2473876817 6547355.01519722, 928822."
        "8297488021 6547373.85047498))",
        "POLYGON ((928801.3037170774 6547237.967399716, 928802.6490940602 654"
        "7250.075792562, 928821.4843718193 6547247.385038597, 928833.59276466"
        "46 6547236.622022734, 928837.6288956129 6547225.8590068715, 928843.0"
        "104035441 6547213.750614027, 928847.0465344925 6547190.879205319, 92"
        "8821.4843718193 6547185.497697388, 928789.1953242321 6547180.1161894"
        "57, 928801.3037170774 6547237.967399716))",
        "POLYGON ((928594.1156617263 6547063.068391953, 928619.6778243994 654"
        "7103.429701437, 928657.3483799178 6547094.012062557, 928657.34837991"
        "78 6547036.160852297, 928607.5694315543 6547032.124721348, 928594.11"
        "56617263 6547063.068391953))",
        "POLYGON ((928903.5523677701 6547065.759145918, 928925.0783994949 654"
        "7081.903669712, 928949.2951851853 6547053.650753073, 928942.56830027"
        "13 6547014.634820572, 928903.5523677701 6547013.28944359, 928887.407"
        "8439765 6547041.5423602285, 928903.5523677701 6547065.759145918))",
        "POLYGON ((928991.001871652 6547346.942935323, 929020.6001652736 6547"
        "338.870673426, 929032.7085581188 6547309.272379805, 928993.692625617"
        "6 6547297.16398696, 928973.5119708757 6547305.236248856, 928962.7489"
        "550132 6547324.071526616, 928991.001871652 6547346.942935323))",
        "POLYGON ((929038.09006605 6547208.369106095, 929059.6160977747 65472"
        "04.332975147, 929085.1782604479 6547169.353173594, 929060.9614747575"
        " 6547138.40950299, 929040.7808200156 6547130.337241093, 929008.49177"
        "24284 6547143.791010921, 929011.182526394 6547173.389304543, 929038."
        "09006605 6547208.369106095))"
    ]


import laspy
import numpy as np
from numpy.random import random_sample

def gen_synthetic_LasData(x_start, y_start, length=10):
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
    mock_hdr.mins, mock_hdr.maxs = [Xmin,Ymin,Zmin], [Xmax,Ymax,Zmax]

    mock_las = laspy.LasData(mock_hdr)
    mock_las.X, mock_las.Y, mock_las.Z = allX, allY, allZ

    return mock_las


@pytest.fixture
def deliveries(tmp_path):
    output_path = tmp_path / 'deliv1'
    output_path.mkdir(exist_ok=True)

    length = 10

    las1 = gen_synthetic_LasData(length=length)
    las1.classification=np.ones(length)
    las1.write( output_path / f'{las1.mins[0]}_{las1.maxs[1]}.laz')

    las2 = gen_synthetic_LasData(length=length)
    las2.classification=np.ones(length)
    las2.write( output_path / f'{las2.mins[0]}_{las2.maxs[1]}.laz')

    # TODO: add a third file with different nb of points
    return output_path

def gen_test_las(output_path, x=None, y=None, classification=np.ones(10)):
    """Generates a small test LAS file using laspy 2.x.

    Returns:
        pathlib.Path: path to generated LAS file 
    """
    
    allX = np.array( x )
    allY = np.array( y )
    allZ = np.zeros( len(x) )

    Xmin, Ymin, Zmin = ( np.min(allX),
                         np.min(allY),
                         np.min(allZ) )

    Xmax, Ymax, Zmax = ( np.max(allX),
                         np.max(allY),
                         np.max(allZ) )

    test_hdr = laspy.LasHeader(version="1.2", point_format=1)
    test_hdr.offsets = [Xmin,Ymin,Zmin]
    test_hdr.scales = [0.001,0.001,0.001]
    test_hdr.mins = [Xmin,Ymin,Zmin]
    test_hdr.maxs = [Xmax,Ymax,Zmax]

    test_las = laspy.LasData(test_hdr)

    test_las.X = allX
    test_las.Y = allY
    test_las.Z = allZ
    print(test_las.X, test_las.Y, test_las.x, test_las.y)
    test_las.classification = classification

    

    test_las.write(write_path)
    return write_path
    

@pytest.fixture
def delivery1(tmp_path):
    output_path = tmp_path / 'deliv1'
    gen_test_las(
        output_path,
        x=test_coords['las1']['x'],
        y=test_coords['las1']['y'], 
        classification=np.ones(len( test_coords['las1']['x'] ))
    )
    gen_test_las(
        output_path,
        x=test_coords['las2']['x'],
        y=test_coords['las2']['y'],
        classification=np.ones(len( test_coords['las2']['x'] ))
    )
    # TODO: add a third file with different nb of points
    return output_path


@pytest.fixture
def delivery2(tmp_path):
    output_path = tmp_path / 'deliv2'
    gen_test_las(
        output_path,
        x=test_coords['las1']['x'],
        y=test_coords['las1']['y'], 
        classification=[2,2,2,1,2,2]
    )
    gen_test_las(
        output_path,
        x=test_coords['las2']['x'],
        y=test_coords['las2']['y'],
        classification=[1,1,1,2]
    )
    # TODO: add a third file with different nb of points
    return output_path


@pytest.fixture
def vect_ref(tmp_path):
    output_path = tmp_path / 'report'
    output_path.mkdir(exist_ok=True)
    polygons = [shapely.wkt.loads(p) for p in test_polygons_wkt]
    polygons_gdf = gpd.GeoDataFrame(geometry=polygons, crs='EPSG:2154')
    polygons_gdf.to_file(output_path / 'vect_ref.gpkg')
    return output_path / 'vect_ref.gpkg'

    
def test_compare_deliveries(tmp_path, delivery1, delivery2, vect_ref):    
    output_path = tmp_path / 'output'
    crs = 'EPSG:2154'
    
    delivery_comparator = DeliveryComparator(
        delivery1,
        delivery2,
        vect_ref,
        output_path,
        crs = crs 
    )
    delivery_comparator.compare()

    
    dirs = [p.name for p in output_path.iterdir() if p.is_dir()]
    files = [p.name for p in output_path.iterdir() if p.is_file()]

    # Assert right folders created
    for d in ['missing_changes', 'comparison_report']:
        assert d in dirs
    
    # Assert right files created
    for p in delivery1.iterdir():
        if p.is_file():
            assert f"change_map_{p.stem}.shp" in files

    # Assert geometries present in "missing_changes" are indeed missing changes
    list_missing_polygs = []
    for mc in (output_path / 'missing_changes').iterdir():
        if mc.suffix == '.shp':
            list_missing_polygs.append(gpd.read_file(mc))
    missing_polygs = pd.concat(list_missing_polygs)
    assert len(missing_polygs) == 4
    # Assert geometries present in "change_map"
    # Assert correctness of statistics