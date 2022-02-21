import laspy
import rasterio
from pathlib import Path
from .cleaning import CleaningProcess

class ReclassifyAbove(CleaningProcess):
    def init(
            self,
            dtm,
            base_class,
            new_class,
            threshold
        ):
        """Change classification if point is above a certain altitude threshold over
        a DTM (Digital Terrain Model)

        Args:
            dtm (str, pathlib.Path or rasterio.io.DatasetReader): Digital Terrain Model
                as raster data. Either a path to the dataset or a Python object
                representing the dataset.
            las (str, pathlib.): LAS file to process. Either a path to the dataset or
                a Python object representing the dataset. 
            base_class (int): classification value for which a reclassification is
                being considered.
            new_class (int): If point meets criterion (being above the provided
                `threshold` and part of the `base class`), its classification is changed
                to `new_class`.
            threshold (float): altitude limit to perform the reclassification 
            output_folder (_type_, optional): _description_. Defaults to None.
            output_suffix (_type_, optional): _description_. Defaults to None.

        Raises:
            TypeError: _description_
        """
        if isinstance(dtm, str) or isinstance(dtm, Path):
            print(f"Opening {dtm}...")
            dtm = rasterio.open(dtm)
        elif not isinstance(dtm, rasterio.io.DatasetReader):
            raise TypeError(f"dtm should be a str, a pathlib.Path or a rasterio.io.DatasetReader")