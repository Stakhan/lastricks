import numpy as np
from laspy import LasData, ExtraBytesParams
from ..core import LASProcessor, LASProcess

class ErrorCloud(LASProcess):
    def __init__(
            self,
            error_label=1,
            correct_label=0,
            map_awaited={
                1: 1,
                2: 2,
                3: 4,
                4: 4,
                5: 4,
                6: 6,
                9: 9,
                17: 17,
                64: 64,
                65: 65
                }
        ):
        """Generates a new point record named `error_cloud` in which the  
           presence/absence of error is saved as a binary mask. A point is
           considered erroneous when its classificaiton value differs from
           the one in the ground truth.
        Args:
            error_label (int): value associated to the presence of an error.
                Defaults to 1.
            correct_label (int): value associated to the absence of error.
                Defaults to 0.
            map_awaited (dict): a mapping to adjust the ground truth values
                in order to reflect the actual awaited values in the tested
                LAS/AZ representation. Default is the mapping for FR_LHD
                project.
        """
        assert 0 <= error_label <= 255
        assert 0 <= correct_label <= 255
        assert error_label != correct_label

        self.matcher = {  True: error_label,
                         False: correct_label }
        self.map_awaited = map_awaited

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
        las_classif = self.remove_virtual_points(las.classification)
        las_ref_classif_raw = self.remove_virtual_points(las_ref.classification)
        nb_vrt_pts = len(las.classification) - len(las_classif)
        try:
            las_ref_classif = np.vectorize(self.map_awaited.get)( las_ref_classif_raw )
        except Exception:
            enc_vals = np.unique(las_ref_classif_raw)
            poss_keys = list(self.map_awaited.keys())
            missing = [k for k in enc_vals if k not in poss_keys]
            raise KeyError(
                f"The following values have been encountered: {missing}, "
                f"But no corresponding key in 'map_awaited' exists: {poss_keys}")
        print('sizes after adjustments', len(las_classif), len(las_ref_classif))
        print('unique values after adjustments', np.unique(las_classif), np.unique(las_ref_classif))
        assert len(las_classif) == len(las_ref_classif)

        mask = las_classif != las_ref_classif

        las.add_extra_dim(
            ExtraBytesParams(
                    name=f"error_mask",
                    type=np.uint8,
                    description=f"Binary error mask"
            )
        )

        las['error_mask'] = np.concatenate((
            np.vectorize(self.matcher.get)( mask ),
            np.full((nb_vrt_pts,), self.matcher[False], dtype=int)
        ))
        return las

    def remove_virtual_points(self, classification):
        classification = np.array(classification)
        if 66 in classification:
            mask = classification != 66
            print(f"Removing {sum(~mask)} virtual points")
            return classification[ mask ]
        else:
            return classification

    def get_type(self):
        return LASProcessType.DoubleInput