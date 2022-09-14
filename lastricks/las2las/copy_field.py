import sys
import argparse
import numpy as np
from pathlib import Path
from inspect import signature
from laspy import LasData, ExtraBytesParams
from ..core import LASProcessor, LASProcess, LASProcessType

class CopyField(LASProcess):
    def __init__(
            self,
            payload,
            target,
            create_dim_if_needed = False,
            scale_payload=True
        ):
        """Copy the content of `payload` field into `target` field. The
           content of `target` will be overwritten by the one of `payload`.

        Args:
            payload (str): name of the field whose content will be copied
            target (str): name of the field where the new content will arrive
            create_dim_if_needed (bool): if `target` dim doesn't exist in the
                `laspy.LasData` representation, create it. Defaults to False.
            scale_payload (bool): whether `payload` should be scaled to fit
                in `target` available range.
        """
        self.payload = payload
        self.target = target
        self.create_dim_if_needed = create_dim_if_needed
        self.scale_payload = scale_payload

    def __call__(self, las: LasData) -> LasData:
        """Process a single set of LAS/LAZ point clouds.

            Args:
                las (laspy.LasData): point cloud on which the field change
                    should be performed

            Returns:
                laspy.LasData: same as `las` but with the correct field
                    content moved to the right location.
        """
        assert self.payload in list(las.point_format.dimension_names)
        target_present = self.target in list(las.point_format.dimension_names)
        payload_infos = las.point_format.dimension_by_name(self.payload)
        target_infos = las.point_format.dimension_by_name(self.target)

        if not self.create_dim_if_needed:
            assert target_present
        else:
            if not target_present:
                las.add_extra_dim(
                    ExtraBytesParams(
                        name=self.target,
                        type=payload_infos.dtype,
                        description=payload_infos.description
                    )
                )

        try:
            assert las[self.target].max() >= las[self.payload].max()
            assert las[self.target].min() <= las[self.payload].min()
        except:
            if self.scale_payload:
                offset = abs(las[self.payload].min())
                scale = abs(las[self.payload].max()-las[self.payload].min())/2**target_infos.num_bits
                print(f"scaling all {self.payload} values to fit in {self.target}")
                las[self.payload] += offset
                las[self.payload] /= scale
            else:
                raise ValueError(
                    f"{self.target} doesn't have enough room to store"
                    f" {self.payload}. Try setting the 'scale_payload'"
                    f" flag to True.")
        
        las[self.target] = las[self.payload]

        return las     

    def get_type(self):
        return LASProcessType.SingleInput

def parse_args(arguments):
    "Parse arguments and check their integrity."
    parser = argparse.ArgumentParser(
        description=CopyField.__doc__)
    parser.add_argument(
        '-i', '--input-path',
        help='directory containing data to process',
        required=True)
    parser.add_argument(
        '-o', '--output-path',
        help="directory in which the processed data should be saved",
        required=True)
    for param in signature(CopyField.__init__).parameters.values():
        if param.name != 'self':
            norm_name = param.name.lower().replace('_', '-')
            parser.add_argument(
                f'-{norm_name[0]}', f'--{norm_name}'
                )
    
    args = parser.parse_args(arguments)

    args.input_path = Path(args.input_path).resolve()
    args.output_path = Path(args.output_path).resolve()

    
    assert args.input_path.is_dir()
    assert args.output_path.is_dir()

    return args

if __name__ == '__main__':
    args = vars(parse_args(sys.argv[1:]))

    cf = CopyField(
        args['payload'],
        args['target'],
        create_dim_if_needed= False if args['create_dim_if_needed'] is None else args['create_dim_if_needed']
        )

    from ..core import LASProcessor

    processor = LASProcessor(
        args['input_path'],
        pipeline = [cf],
        output_folder = args['output_path'],
        rejection_mechanism = False
    )
    processor.run()