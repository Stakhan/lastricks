"""
/!\\ These tests are meant to be used with laspy 2.x
"""
import sys
import laspy
import pytest
from pathlib import Path

root_path = Path(__file__).parent.resolve()

sys.path.insert(0, str(root_path.parents[1]))
from lastricks.core import InputManager


@pytest.fixture
def mock_input_manager(folder_mock_las):
    return InputManager( folder_mock_las)

def test_get_las_paths(mock_input_manager):
    expected = [mock_input_manager.input_path/f"mock_{i}.las" for i in range(3)]
    obtained = mock_input_manager.get_las_paths()
    for i in range(3): 
        assert  sorted(obtained)[i] == sorted(expected)[i]

def test_len(mock_input_manager):
    assert len(mock_input_manager) == 3

def test_query_las_path(mock_input_manager, tmp_path):
    with pytest.raises(FileNotFoundError):
        # `test_file` needs to be created because 
        # function verifies file existence
        test_file = tmp_path / 'inexistant.las'
        test_file.touch() 
        mock_input_manager.query_las_path(test_file)
    with pytest.raises(Exception):
        test_file = tmp_path / 'mock_.laz'
        test_file.touch()
        mock_input_manager.query_las_path(test_file)

    expected = mock_input_manager.input_path / 'mock_1.las'
    
    test_file = tmp_path / 'mock_1_c.laz'
    test_file.touch()
    assert mock_input_manager.query_las_path(test_file) == expected
    test_file = tmp_path / 'mock_1.laz'
    test_file.touch()
    assert mock_input_manager.query_las_path(test_file) == expected
    test_file = tmp_path / '1.laz'
    test_file.touch()
    assert mock_input_manager.query_las_path(test_file) == expected