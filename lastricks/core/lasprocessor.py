import time
import laspy
import shutil
import traceback
from pathlib import Path
from laspy import LasData
from datetime import timedelta
from abc import ABC, abstractmethod
from .input_manager import InputManager


class LASProcessor:
    """General structure for easy LAS/LAZ files processing from
       a sequence of `lastricks.lasprocessor.LASProcess`.
       Handles both a single file or a folder of files.
       
       For more complex inputs (such as auxiliary input from
       `other_input_paths`), it is possible to write a custom
       kernel function that will be applied on each LAS/LAZ file.
    """

    def __init__(
        self,
        main_input_path: Path,
        *other_input_paths: Path,
        kernel_func: 'function' = None,
        pipeline: list = None,
        output_folder: Path = None,
        output_suffix: str = None,
        rejected_folder: Path = None,
        rejection_mechanism: bool = True
        ) -> None:
        """
        Args:
            main_input_path (Path): file or directory of files to process.
            *other_input_paths (*Path): helper files or directories.
            pipeline (list(lastricks.LASProcess)): list of processes to use.
                If used, no `kernel_func` should be provided.
            kernel_func (function): function to apply on each LAS/LAZ file
                from `main_input_path`. See `LASProcessor.default_kernel_func`
                for awaited function signature.
            output_folder (str or Path, optional): Target destination for
                result LAS/LAZ files. If `None`, defaults to
                `main_input_path`.
            output_suffix (str, optional): Suffix appended to result filename.
                Shouldn't contain any dots. If `None`, defaults to
                '_processed'.
            output_folder (str or Path, optional): Target destination for
                rejected files if rejection_mechanism is `True`. A file is
                rejected when a process applied to it raises an error. If
                `None`, defaults to a folder named `rejected` inside
                `main_input_folder`.
            rejection_mechanism (bool): whether rejection mechanism is
                activated or not. A file is rejected when a process applied
                to it raises an error. Defaults to True. 
        """
        if pipeline and kernel_func:
            raise ValueError( "You have to provide either a pipeline or"
                              " a kernel function. Both is not acceptable." )
        elif pipeline:
            assert len(pipeline) > 0 
            self.pipeline = pipeline
            print(
                "LASProcessor object created with following "
                +"LASProcess(es):\n--> "
                +"\n--> ".join([str(p) for p in pipeline])+"\n"
                )
            self.kernel_func = self.default_kernel_func            
        elif kernel_func:
            self.kernel_func = kernel_func
        else:
            raise ValueError("At least a pipeline or a kernel function "
                             "must be provided for a LASProcessor "
                             "instance to properly work.")
        
        self.main_input = InputManager(main_input_path)
        self.other_inputs = [ 
            InputManager(oip) for oip in other_input_paths
            if oip.exists()
            ]
        self.output_folder = self.determine_output_folder( output_folder )
        self.rejected_folder = self.determine_rejected_folder(rejected_folder)
        self.output_suffix = self.determine_suffix(output_suffix)
        self.rejection_mechanism = rejection_mechanism

    def determine_output_folder(self, output_folder: Path) -> Path:
        if output_folder:
            assert output_folder.exists()
            return output_folder
        elif not output_folder:
            return self.main_input.directory()
    
    def determine_rejected_folder(self,rejected_folder: Path) -> Path:
        if rejected_folder:
            assert rejected_folder.exists()
            return rejected_folder
        elif not rejected_folder:
            return self.main_input.directory() / 'rejected'

    def determine_suffix(self, output_suffix) -> None:  
        if (not output_suffix) and self.main_input.directory() == self.output_folder:
            return  "_processed"
        elif not output_suffix:
            return ''
        elif output_suffix:
            assert '.' not in output_suffix
            return output_suffix

    def default_kernel_func(
        self,
        path: Path,
        main_input: InputManager,
        *other_inputs: InputManager
        ) -> LasData:
        las = laspy.read(path)
        for proc in self.pipeline:
            las = proc(las)
        return las

    def handle_rejected(self, path: Path, err: Exception) -> None:
        if not self.rejected_folder.exists():
            self.rejected_folder.mkdir()
        print('-'*79)
        print(traceback.format_exc())
        print('-'*79)
        shutil.move(
            path,
            self.rejected_folder / path.name
        )
        print(f"{type(err).__name__} occured. {path.stem} got "
            f"moved to '{self.rejected_folder}'")
        print('-'*79)

    def run(self) -> None:
        for i, path in enumerate(self.main_input):
            outlas_path = self.output_folder / (path.stem+self.output_suffix+path.suffix)
            
            if not outlas_path.exists():
                startt = time.time()

                print(f"[{i+1}/{len(self.main_input)}] Processing {path.name}...")

                try:
                    las = self.kernel_func(
                        path,
                        self.main_input,
                        *self.other_inputs
                        )
                except Exception as e:
                    if self.rejection_mechanism:
                        self.handle_rejected(path, e)
                        continue
                    else:
                        raise e

                print(f"Writting to {outlas_path}")
                las.write( outlas_path )

                print(f"-- Processing time: {timedelta(seconds=time.time()-startt)}")
            else:
                print(f"Skipping {path.stem} (already processed)")
                