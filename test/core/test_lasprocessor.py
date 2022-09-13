"""
/!\\ These tests are meant to be used with laspy 2.x
"""
import sys
import laspy
import pytest
import shutil
import numpy as np
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

class MockLASProcessDoubleInput(ltc.LASProcess):
    def __init__(self, idx):
        self.idx = idx

    def __call__(self, las1, las2):
        print(f"Applying mock process #{self.idx}...")
        las1.classification = (
            np.array(las1.classification)
            + np.array(las2.classification)
        )
        return las1

    def get_type(self):
        return ltc.LASProcessType.DoubleInput

@pytest.fixture
def mock_lasprocess_pipeline():
    return [MockLASProcess(i) for i in range(3)]  


def test_processor_single_file_default(
    mock_lasprocess_pipeline,
    mock_las
    ):
    processor = ltc.LASProcessor(
        mock_las,
        pipeline=mock_lasprocess_pipeline,
    )

    processor.run()
    expected_output = (mock_las.parent / f"{mock_las.stem}_processed{mock_las.suffix}")
    assert expected_output.exists()


def test_processor_single_file_alt_output_folder(
    mock_lasprocess_pipeline,
    mock_las,
    tmp_path
    ):
    processor = ltc.LASProcessor(
        mock_las,
        pipeline=mock_lasprocess_pipeline,
        output_folder=tmp_path
        )

    processor.run()
    expected_output = (tmp_path / mock_las.name)
    assert expected_output.exists()


def test_processor_single_file_alt_output_suffix(
    mock_lasprocess_pipeline,
    mock_las
    ):
    processor = ltc.LASProcessor(
        mock_las,
        pipeline=mock_lasprocess_pipeline,
        output_suffix='_alt_suffix'
        )

    processor.run()
    expected_output = mock_las.parent / f"{mock_las.stem}_alt_suffix{mock_las.suffix}"
    assert expected_output.exists()


def test_processor_single_file_alt_output_folder_and_suffix(
    mock_lasprocess_pipeline,
    mock_las,
    tmp_path
    ):
    processor = ltc.LASProcessor(
        mock_las,
        pipeline=mock_lasprocess_pipeline,
        output_folder=tmp_path,
        output_suffix='_alt_suffix'
        )

    processor.run()
    expected_output = tmp_path / f"{mock_las.stem}_alt_suffix{mock_las.suffix}"
    assert expected_output.exists()


def test_processor_dir_default(
    mock_lasprocess_pipeline,
    folder_mock_las
    ):
    processor = ltc.LASProcessor(
        folder_mock_las,
        pipeline=mock_lasprocess_pipeline,
        )

    processor.run()
    for i in range(3):
        expected_output = (folder_mock_las / f"mock_{i}.las")
        assert expected_output.exists()


def test_processor_single_file_default_kernel_func(
    mock_las,
    tmp_path
    ):

    mock_lasprocess = MockLASProcessDoubleInput(0)
    def custom_kernel_func(path, main_input, other_input):
        las = main_input.query_las(path)
        gt_las = other_input.query_las(path)
        return mock_lasprocess(las, gt_las)

    mock_las_2 = tmp_path / mock_las.name
    shutil.copy(
        mock_las,
        tmp_path / mock_las.name
    )
    processor = ltc.LASProcessor(
        mock_las,
        mock_las_2,
        kernel_func=custom_kernel_func,
        )

    processor.run()
    expected_output = (mock_las.parent / f"{mock_las.stem}_processed{mock_las.suffix}")
    assert expected_output.exists()