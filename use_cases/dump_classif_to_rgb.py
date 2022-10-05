import numpy as np
from pathlib import Path
from lastricks.core import LASProcess, LASProcessor, LASProcessType



class DumpClassifToRGB(LASProcess):
    def __init__(self, mapping=None):
        assert mapping is not None
        self.mapping = mapping
    
    def __call__(self, las):
        reds, greens, blues = [], [], []
        for c in las.classification:
            rgbs = self.mapping[c]
            reds.append(   rgbs[0] )
            greens.append( rgbs[1] )
            blues.append(  rgbs[2] )
        print(np.unique(reds), np.unique(las.classification))
        las.red = reds
        las.green = greens
        las.blue = blues
        return las
    
    def get_type(self):
        return LASProcessType.SingleInput

if __name__ == '__main__':
    input_path = Path(r"C:\Users\EAL\OneDrive - ESRI BELUX NV\Documents\Visuals\05_materials\training_samples")

    cleaning_pipeline = [
        DumpClassifToRGB(mapping={
            1: (255,255,255),
            2: (181, 101, 29),
            3: (144, 238, 144),
            4: (144, 238, 144),
            5: (144, 238, 144),
            6: (255, 0, 0)
        })
    ]
    processor = LASProcessor(
        input_path,
        pipeline=cleaning_pipeline,
        output_suffix='_classif',
        rejection_mechanism=False
    )

    processor.run()
    
