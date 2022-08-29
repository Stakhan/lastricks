from .. import LASProcessor, LASProcess

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
            ref_classif_location (str, pathlib.Path): folder containing a
                ground truth file for each of the file processed by this
                `LASProcess`.
            error_label (int): value associated to the presence of an error.
            correct_label (int): value associated to the absence of error.
        """
        #self.ref_classif_loc = Path(ref_classif_location)
        self.error_label = error_label
        self.correct_label = correct_label

    def __call__(self, las):
        """Process a single python representation of a LAS/LAZ file.

            Args:
                las (laspy.LasData): LAS/LAZ file representation to process

            Returns:
                laspy.LasData: the resulting representation
        """
        pass