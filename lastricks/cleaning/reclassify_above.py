import laspy
import tempfile
import rasterio
import numpy as np
from pathlib import Path
from rasterio.mask import mask
from shapely.geometry import Polygon
from ..core import LASProcess, LASProcessType


class ReclassifyAbove(LASProcess):
    def __init__(
            self,
            dtm,
            base_class,
            new_class,
            threshold
        ):
        """Change classification if point is above a certain altitude threshold over
        a DTM (Digital Terrain Model)

        Args:
            dtm (str, pathlib.Path or rasterio.io.DatasetReader): Digital Terrain
                Model as raster data. Either a path to the dataset or a Python object
                representing the dataset.
            base_class (int): classification value for which a reclassification is
                being considered.
            new_class (int): If point meets criterion (being above the provided
                `threshold` and part of the `base class`), its classification is
                changed to `new_class`.
            threshold (float): altitude limit in meters to perform the
                reclassification. 
   
        Raises:
            TypeError: when dtm isn't provided in a sound manner
        """
        if isinstance(dtm, str) or isinstance(dtm, Path):
            print(f"Opening {dtm}...")
            self.dtm = rasterio.open(dtm)
        elif isinstance(dtm, rasterio.io.DatasetReader):
            self.dtm = dtm
        else:
            raise TypeError(f"dtm should be a str, a pathlib.Path or a rasterio.io.DatasetReader")
        
        self.base_class = base_class
        self.new_class = new_class
        self.threshold = threshold

        self.cache = Path(tempfile.TemporaryDirectory().name) / 'lastricks_cache'
        self.cache.mkdir(exist_ok=True, parents=True)
        
        
    def __call__(self, las):
        """Process a single python representation of a LAS/LAZ file.

        Args:
            las (laspy.LasData): LAS/LAZ file representation to process

        Returns:
            laspy.LasData: the resulting representation
        """
        base_class_mask = las.classification == self.base_class
        base_class_z = np.array(las.z)[base_class_mask]
        base_class_idxs = np.where(base_class_mask)[0]

        dtm_aoi = self.crop_dtm_to_aoi(las)

       # Adjusting z values based on DTM 
        for i in range( len(base_class_z) ):
            px, py = dtm_aoi.index(las.x[i], las.y[i])
            base_class_z[i] -= dtm_aoi.read(1)[px,py]
        
        modified_classif = np.array(las.classification)
       # Actually changing the classification based on criterion 
        modified_classif[ base_class_idxs[base_class_z >= self.threshold] ] = self.new_class
        las.classification = modified_classif

        return las

    def get_type(self):
        return LASProcessType.SingleInput

    def crop_dtm_to_aoi(self, las):
        """Crops our nation-wide Digital Terrain Model (DTM) to the las
           Area Of Interest (AOI).

        Args:
            las (laspy.LasData): LAS/LAZ file representation to process
        Returns:
            rasterio.io.DatasetReader: the cropped dtm representation
        """
        lasfile_hold = Polygon([
            (las.header.mins[0], las.header.mins[1]),
            (las.header.maxs[0], las.header.mins[1]),
            (las.header.maxs[0], las.header.maxs[1]),
            (las.header.mins[0], las.header.maxs[1])
        ])

        out_image, out_transform = mask(self.dtm, [lasfile_hold], crop=True)
        out_meta = self.dtm.meta
        out_meta.update({"driver": "GTiff",
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform})
        
        with rasterio.open(self.cache / "dtm_aoi.tif", "w", **out_meta) as dest:
            dest.write(out_image) 
        
        return rasterio.open(self.cache / "dtm_aoi.tif")
    