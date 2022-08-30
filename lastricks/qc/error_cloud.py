import numpy as np
from laspy import LasData, ExtraBytesParams
from ..core import LASProcessor, LASProcess

class ErrorCloud(LASProcess):
    def __init__(
            self,
            error_label=1,
            correct_label=0
        ):
        """Generates a new point record named `error_cloud` in which the  
           presence/absence of error is saved as a binary mask. A point is
           considered erroneous when its classificaiton value differs from
           the one in the ground truth.
        Args:
            error_label (int): value associated to the presence of an error.
            correct_label (int): value associated to the absence of error.
        """
        assert 0 <= error_label <= 255
        assert 0 <= correct_label <= 255
        assert error_label != correct_label

        self.matcher = {  True: error_label,
                         False: correct_label }

    def __call__(self, las: LasData, las_ref: LasData):
        """Process a single set of LAS/LAZ point clouds.

            Args:
                las (laspy.LasData): point cloud in which errors should
                    be spotted.
                las_ref (laspy.LasData): reference (groud truth) point
                    cloud to spot the errors.

            Returns:
                laspy.LasData: same as `las` but with an error mask highlighting
                    the errors in a new point record.
        """
        mask = las.classification != las_ref.classification

        las.add_extra_dim(
            ExtraBytesParams(
                    name=f"error_mask",
                    type=np.uint8,
                    description=f"Binary error mask"
            )
        )
        las['error_mask'] = np.vectorize(self.matcher.get)( mask )
        return las

    def get_type(self):
        return LASProcessType.DoubleInput