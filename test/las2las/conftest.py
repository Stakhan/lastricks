import pytest
from numpy.random import random_sample
from ..lasdata_generator import generate_LasData

@pytest.fixture
def las6():
    """LAS representation with an intensity field different from the
       classification field.
    """
    las6 = generate_LasData(length=11)
    las6.classification = [1,2,3,4,5,6,9,17,64,65,66]
    las6.intensity = random_sample(size=(11,))*100
    yield las6