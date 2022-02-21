"""
/!\\ These tests are meant to be used with laspy 2.x
"""
import sys
import laspy
import pytest
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks.cleaning as ltc
from .common_fixtures_v2 import mock_las_v2, folder_mock_las_v2, mock_dtm


class MockCleaning(ltc.CleaningProcess):
    def __init__(self, idx):
        self.idx = idx

    def __call__(self, las):
        print(f"Applying mock cleaning #{self.idx}...")
        return las


@pytest.fixture
def mock_cleaning_pipeline():
    return [MockCleaning(i) for i in range(3)]  


def test_cleaner_single_file_default(
    mock_cleaning_pipeline,
    mock_las_v2
    ):
    cleaner = ltc.Cleaner(
        mock_las_v2,
        mock_cleaning_pipeline
        )

    cleaner.clean()
    expected_output = (mock_las_v2.parent / f"{mock_las_v2.stem}_cleaned{mock_las_v2.suffix}")
    print(expected_output)
    assert expected_output.exists()