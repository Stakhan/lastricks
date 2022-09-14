import sys
import argparse
import numpy as np
from pathlib import Path
from inspect import signature
from laspy import LasData, ExtraBytesParams, DimensionKind
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
        self.scale_payload = bool(scale_payload)

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
        if target_present:
            target_infos = las.point_format.dimension_by_name(self.target)
        elif not target_present and self.create_dim_if_needed:
            las.add_extra_dim(
                ExtraBytesParams(
                    name=self.target,
                    type=payload_infos.dtype,
                    description=payload_infos.description
                )
            )
        else:
            raise ValueError(
                f"Dimension {self.target} does not exist.\n"
                f"Existing dimensions "
                f"are: {list(las.point_format.dimension_names)}")
        
        target_infos = las.point_format.dimension_by_name(self.target)

        try:
            self.handle_type_fitting(las, target_infos)
        except ValueError as e:
            if self.scale_payload:
                scaled_payload = self.payload_scaling(las, target_infos)
                
            else:
                raise e
        else:
            scaled_payload = las[self.payload]

        las[self.target] = scaled_payload
        return las    

    def get_type(self):
        return LASProcessType.SingleInput

    def target_min_max(self, target_infos):
        if target_infos.kind in [DimensionKind.SignedInteger,
                                 DimensionKind.UnsignedInteger]:
            target_min = np.iinfo(target_infos.dtype).min
            target_max = np.iinfo(target_infos.dtype).max
        elif target_infos.kind is DimensionKind.FloatingPoint:
            target_min = np.finfo(target_infos.dtype).min
            target_max = np.finfo(target_infos.dtype).max
        elif target_infos.kind is DimensionKind.BitField:
            target_min = 0
            target_max = 1
        else:
            raise NotImplementedError(f"No way to handle target of type '{target_infos.dtype.name}' yet.")
        return target_min, target_max

    def handle_type_fitting(self, las, target_infos):
        t_min, t_max = self.target_min_max(target_infos)
        pl_min, pl_max = las[self.payload].min(), las[self.payload].max()
        
        print('payload range:', pl_min, pl_max)
        print(' target range:', t_min, t_max)
        
        try:
            assert t_max >= pl_max
            assert t_min <= pl_min
        except AssertionError:
            raise ValueError(
                    f"{self.target} (in [{pl_min}, {pl_max}]) doesn't have"
                    f" enough room to store {self.payload} (in [{t_min},"
                    f" {t_max}]). Try setting the 'scale_payload' flag to"
                    f" True.")
        
    def payload_scaling(self, las, target_infos):
        t_min, t_max = self.target_min_max(target_infos)
        pl_min, pl_max = las[self.payload].min(), las[self.payload].max()
        offset = abs()
        scale = abs(pl_max-pl_min)/2**target_infos.num_bits
        print(f"scaling all {self.payload} values in [{pl_min}, {pl_max}]"
              f"to fit in {self.target} range [{t_min}, {t_max}]")
        scaled_payload = las[self.payload] + offset
        scaled_payload /= scale
        return scaled_payload

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
    print(args)

    if args['scale_payload'] is None:
        scale_payload = True
    else:
        scale_payload = False
    if args['create_dim_if_needed'] is None:
        create_dim_if_needed = False
    else:
        create_dim_if_needed = True

    cf = CopyField(
        args['payload'],
        args['target'],
        create_dim_if_needed = create_dim_if_needed, # False if args['create_dim_if_needed'] is None else args['create_dim_if_needed'],
        scale_payload = scale_payload
        )

    from ..core import LASProcessor

    processor = LASProcessor(
        args['input_path'],
        pipeline = [cf],
        output_folder = args['output_path'],
        rejection_mechanism = False
    )
    processor.run()