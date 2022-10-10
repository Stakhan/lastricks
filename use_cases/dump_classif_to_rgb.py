import numpy as np
from pathlib import Path
from lastricks.core import LASProcess, LASProcessor, LASProcessType



class DumpClassifToRGB(LASProcess):
    """Write classification (from classification field) inside red, green
    and blue fields.
    """
    def __init__(self, mapping=None):
        """
        Args:
            mapping (dict): Mapping between class number and RGB color (as
            tuple of percentages expressed between 0 and 1). Defaults to None.
        """
        assert mapping is not None
        for value in mapping.values():
            for i in range(3):
                assert 0 <= value[0] <= 1
        # The percentage is converted to a color ranging from 0 to 2**16
        crange = 2**16 - 1
        self.mapping = {
            key: (value[0]*crange, value[1]*crange, value[2]*crange)
            for key,value in mapping.items()
            }

    def __call__(self, las):
        reds, greens, blues = [], [], []
        for c in las.classification:
            rgbs = self.mapping[c]
            reds.append(   rgbs[0] )
            greens.append( rgbs[1] )
            blues.append(  rgbs[2] )
        las.red = reds
        las.green = greens
        las.blue = blues
        return las
    
    def get_type(self):
        return LASProcessType.SingleInput

if __name__ == '__main__':
    root_path = Path(r"C:\Users\EAL\OneDrive - ESRI BELUX NV\Documents\Visuals\05_materials\training_samples")
    input_path = root_path / 'rgb_colors'
    output_path = root_path / 'rgb_classif'
    cleaning_pipeline = [
        DumpClassifToRGB(mapping={
            1: (1, 1, 1),
            2: (181/255, 101/255, 29/255),
            3: (144/255, 238/255, 144/255),
            4: (144/255, 238/255, 144/255),
            5: (144/255, 238/255, 144/255),
            6: (1, 0, 0),
            17: (181/255, 101/255, 29/255),
            46: (1, 1, 1),
            47: (1, 1, 1),
            48: (1, 1, 1),
            49: (1, 1, 1),
            50: (1, 1, 1),
            51: (1, 1, 1),
            52: (1, 1, 1),
            53: (1, 1, 1),
            54: (1, 1, 1),
            55: (1, 1, 1),
            56: (1, 1, 1),
            57: (1, 1, 1),
            58: (1, 1, 1),
            64: (1, 1, 1),
            67: (1, 1, 1),
            77: (1, 1, 1),
            46: (1, 1, 1),
            47: (1, 1, 1),
            48: (1, 1, 1),
            49: (1, 1, 1),
            50: (1, 1, 1),
            51: (1, 1, 1),
            52: (1, 1, 1),
            53: (1, 1, 1),
            54: (1, 1, 1),
            55: (1, 1, 1),
            56: (1, 1, 1),
            57: (1, 1, 1),
            58: (1, 1, 1),
            64: (1, 1, 1),
            65: (1, 1, 1),
            67: (1, 1, 1),
            77: (1, 1, 1),
            155: (1, 1, 1)
        })
    ]
    processor = LASProcessor(
        input_path,
        output_folder=output_path,
        pipeline=cleaning_pipeline,
        output_suffix='_classif',
        rejection_mechanism=False
    )

    processor.run()
    
