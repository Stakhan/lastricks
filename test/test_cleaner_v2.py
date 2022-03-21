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
from common_fixtures_v2 import mock_las_v2, folder_mock_las_v2, mock_dtm


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
    assert expected_output.exists()


def test_cleaner_single_file_alt_output_folder(
    mock_cleaning_pipeline,
    mock_las_v2,
    tmp_path
    ):
    cleaner = ltc.Cleaner(
        mock_las_v2,
        mock_cleaning_pipeline,
        output_folder=tmp_path
        )

    cleaner.clean()
    expected_output = (tmp_path / mock_las_v2.name)
    assert expected_output.exists()


def test_cleaner_single_file_alt_output_suffix(
    mock_cleaning_pipeline,
    mock_las_v2
    ):
    cleaner = ltc.Cleaner(
        mock_las_v2,
        mock_cleaning_pipeline,
        output_suffix='_alt_suffix'
        )

    cleaner.clean()
    expected_output = mock_las_v2.parent / f"{mock_las_v2.stem}_alt_suffix{mock_las_v2.suffix}"
    assert expected_output.exists()


def test_cleaner_single_file_alt_output_folder_and_suffix(
    mock_cleaning_pipeline,
    mock_las_v2,
    tmp_path
    ):
    cleaner = ltc.Cleaner(
        mock_las_v2,
        mock_cleaning_pipeline,
        output_folder=tmp_path,
        output_suffix='_alt_suffix'
        )

    cleaner.clean()
    expected_output = tmp_path / f"{mock_las_v2.stem}_alt_suffix{mock_las_v2.suffix}"
    assert expected_output.exists()


def test_cleaner_dir_default(
    mock_cleaning_pipeline,
    folder_mock_las_v2
    ):
    cleaner = ltc.Cleaner(
        folder_mock_las_v2,
        mock_cleaning_pipeline
        )

    cleaner.clean()
    for i in range(3):
        expected_output = (folder_mock_las_v2 / f"mock_{i}.las")
        assert expected_output.exists()

def test_cleaningprocess(mock_las_v2):
    cp = ltc.CleaningProcess()
    las = laspy.read(mock_las_v2)
    with pytest.raises(NotImplementedError) as e_info:
        cp(las)

def test_cleaner_LAZ_output(
    mock_cleaning_pipeline,
    mock_las_v2
    ):
    cleaner = ltc.Cleaner(
        mock_las_v2,
        mock_cleaning_pipeline,
        output_format='laz'
        )
    cleaner.clean()
    expected_output = mock_las_v2.parent / f"{mock_las_v2.stem}_cleaned.laz"
    assert expected_output.exists()

def test_cleaner_wrong_output_format(
    mock_cleaning_pipeline,
    mock_las_v2
    ):
    with pytest.raises(ValueError) as e_info:
        cleaner = ltc.Cleaner(
        mock_las_v2,
        mock_cleaning_pipeline,
        output_format='wrong'
        )