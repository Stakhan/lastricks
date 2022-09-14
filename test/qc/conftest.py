import laspy
import pytest
import numpy as np
from pathlib import Path
from numpy.random import random_sample, randint
from ..lasdata_generator import generate_LasData

@pytest.fixture
def las1():
    las1 = generate_LasData()
    las1.classification = [1,1,2,2,2,2,2,2,2,2]
    yield las1

@pytest.fixture
def las2():
    las2 = generate_LasData()
    las2.classification = [2,2,1,1,2,2,2,2,2,2]
    yield las2

@pytest.fixture
def las3_vp():
    """Same as `las2` but with 3 virtual points at the end"""
    las3 = generate_LasData(length=13)
    las3.classification = [2,2,1,1,2,2,2,2,2,2,66,66,66]
    yield las3

@pytest.fixture
def las4():
    """Example classification values awaited from subcontractor.
    """
    las4 = generate_LasData(length=10)
    las4.classification = [1,2,4,4,4,6,9,17,64,65]
    yield las4

@pytest.fixture
def las5():
    """The same example as `las4` but after transformations for delivery.
       A virtual point was added at the end.
    """
    las5 = generate_LasData(length=11)
    las5.classification = [1,2,3,4,5,6,9,17,64,65,66]
    yield las5