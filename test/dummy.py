from pathlib import Path
import sys
import laspy
sys.path.append('../')
import lastricks.tools as ltt

print('YO')
ltt.new_class_from_gpkg(
        "mock.gpkg",
        "mock2.las",
        1,
        8,
        output_folder=Path.cwd(),
        output_suffix="_wec",
        )