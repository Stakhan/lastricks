import sys
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
from lastricks.ops import concat_las

from ..lasdata_generator import generate_LasData

def test_concat_las():
    las1 = generate_LasData(length=3)
    las2 = generate_LasData(length=4)
    lasc = concat_las(las1, las2)
    assert len(lasc) == 7