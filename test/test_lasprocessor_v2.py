"""
/!\\ These tests are meant to be used with laspy 2.x
"""
import sys
import laspy
import pytest
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parent))
import lastricks as lt


class MockLASProcess(lt.LASProcess):
    def __init__(self, idx):
        self.idx = idx

    def __call__(self, las):
        print(f"Applying mock process #{self.idx}...")
        return las


@pytest.fixture
def mock_lasprocess_pipeline():
    return [MockLASProcess(i) for i in range(3)]  


def test_processor_single_file_default(
    mock_lasprocess_pipeline,
    mock_las_v2
    ):
    processor = lt.LASProcessor(
        mock_las_v2,
        mock_lasprocess_pipeline
        )

    processor.run()
    expected_output = (mock_las_v2.parent / f"{mock_las_v2.stem}_processed{mock_las_v2.suffix}")
    assert expected_output.exists()


def test_processor_single_file_alt_output_folder(
    mock_lasprocess_pipeline,
    mock_las_v2,
    tmp_path
    ):
    processor = lt.LASProcessor(
        mock_las_v2,
        mock_lasprocess_pipeline,
        output_folder=tmp_path
        )

    processor.run()
    expected_output = (tmp_path / mock_las_v2.name)
    assert expected_output.exists()


def test_processor_single_file_alt_output_suffix(
    mock_lasprocess_pipeline,
    mock_las_v2
    ):
    processor = lt.LASProcessor(
        mock_las_v2,
        mock_lasprocess_pipeline,
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
    processor = lt.LASProcessor(
        mock_las_v2,
        mock_lasprocess_pipeline,
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
    processor = lt.LASProcessor(
        folder_mock_las_v2,
        mock_lasprocess_pipeline
        )

    processor.run()
    for i in range(3):
        expected_output = (folder_mock_las_v2 / f"mock_{i}.las")
        assert expected_output.exists()

def test_lasprocess(mock_las_v2):
    cp = lt.LASProcess()
    las = laspy.read(mock_las_v2)
    with pytest.raises(NotImplementedError) as e_info:
        cp(las)