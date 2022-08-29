"""
/!\\ These tests are meant to be used with laspy 2.x
"""
import sys
import laspy
import pytest
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parents[1]))
import lastricks.core as ltc


class MockLASProcess(ltc.LASProcess):
    def __init__(self, idx):
        self.idx = idx

    def __call__(self, las):
        print(f"Applying mock process #{self.idx}...")
        return las

    def get_type(self):
        return ltc.LASProcessType.SingleInput

@pytest.fixture
def mock_lasprocess_pipeline():
    return [MockLASProcess(i) for i in range(3)]  


def test_processor_single_file_default(
    mock_lasprocess_pipeline,
    mock_las_v2
    ):
    processor = ltc.LASProcessor(
        mock_lasprocess_pipeline,
        mock_las_v2
        )

    processor.run()
    expected_output = (mock_las_v2.parent / f"{mock_las_v2.stem}_processed{mock_las_v2.suffix}")
    assert expected_output.exists()


def test_processor_single_file_alt_output_folder(
    mock_lasprocess_pipeline,
    mock_las_v2,
    tmp_path
    ):
    processor = ltc.LASProcessor(
        mock_lasprocess_pipeline,
        mock_las_v2,
        output_folder=tmp_path
        )

    processor.run()
    expected_output = (tmp_path / mock_las_v2.name)
    assert expected_output.exists()


def test_processor_single_file_alt_output_suffix(
    mock_lasprocess_pipeline,
    mock_las_v2
    ):
    processor = ltc.LASProcessor(
        mock_lasprocess_pipeline,
        mock_las_v2,
        output_suffix='_alt_suffix'
        )

    processor.run()
    expected_output = mock_las_v2.parent / f"{mock_las_v2.stem}_alt_suffix{mock_las_v2.suffix}"
    assert expected_output.exists()


def test_processor_single_file_alt_output_folder_and_suffix(
    mock_lasprocess_pipeline,
    mock_las_v2,
    tmp_path
    ):
    processor = ltc.LASProcessor(
        mock_lasprocess_pipeline,
        mock_las_v2,
        output_folder=tmp_path,
        output_suffix='_alt_suffix'
        )

    processor.run()
    expected_output = tmp_path / f"{mock_las_v2.stem}_alt_suffix{mock_las_v2.suffix}"
    assert expected_output.exists()


def test_processor_dir_default(
    mock_lasprocess_pipeline,
    folder_mock_las_v2
    ):
    processor = ltc.LASProcessor(
        mock_lasprocess_pipeline,
        folder_mock_las_v2,
        )

    processor.run()
    for i in range(3):
        expected_output = (folder_mock_las_v2 / f"mock_{i}.las")
        assert expected_output.exists()