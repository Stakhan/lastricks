import time
import laspy
from pathlib import Path
from laspy import LasData
from datetime import timedelta
from abc import ABC, abstractmethod
class LASProcessor:
    """General structure for easy LAS/LAZ files processing from
       a sequence of `lastricks.lasprocessor.LASProcess`.
       Handles both a single file or a folder of files.
    """

    def __init__(
        self,
        pipeline,
        *input_paths,
        output_folder=None,
        output_suffix=None,
        ) -> None:
        """
        Args:
            input_path (str or Path): file or directory of files to process.
            pipeline (list(lastricks.lasprocessor.LASProcess)): list
                of processes 
            output_folder (str or Path, optional): Target destination for
                processing result. Defaults to `None`.
            output_suffix (str, optional): Suffix appended to result filename.
                Shouldn't contain any dots. Defaults to `None`.
        """
        if len(input_paths) == 1:
            self.state = SingleInputState()
            self.state.context = self
        elif len(input_paths) == 2:
            self.state = DoubleInputState()
            self.state.context = self
        else:
            raise ValueError(
                f"No LASProcess supports {len(input_paths)} input paths yet."
                )

        self.manage_folders(
            input_paths,
            output_folder
        )
        self.manage_suffix(output_suffix)

        assert len(pipeline) > 0 
        self.pipeline = pipeline
        print(
            "LASProcessor object created with following LASProcess(es):\n--> "
            +"\n--> ".join([str(p) for p in pipeline])+"\n"
            )

    def manage_folders(
        self,
        input_paths,
        output_folder
        ) -> None:
        self.state.manage_folders(
            input_paths,
            output_folder
        )
            
    def manage_suffix(self, output_suffix) -> None:  
        # Managing output suffix
        if not output_suffix and self.input_folder == self.output_folder:
            self.output_suffix =  "_processed"
        elif not output_suffix:
            self.output_suffix = ''
        elif output_suffix:
            assert '.' not in output_suffix
            self.output_suffix = output_suffix

    def apply_pipeline(self, *las) -> LasData:
        """Apply each `LASProcess` to a LAS/LAZ representation.

        Args:
            las (laspy.LasData): one or more LAS/LAZ representation
                on which pipeline will be applied

        Returns:
            laspy.LasData: resulting LAS/LAZ representation
        """
        return self.state.apply_pipeline(*las)

    def run(self) -> None:
        self.state.run()
        


class LASProcessorState(ABC):

    @property
    def context(self) -> LASProcessor:
        return self._context

    @context.setter
    def context(self, context: LASProcessor) -> None:
        self._context = context

    @abstractmethod
    def apply_pipeline(self, *las: LasData) -> LasData:
        pass

    @abstractmethod
    def manage_folders(self, input_paths, output_folder) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass


class SingleInputState(LASProcessorState):
    
    def apply_pipeline(self, las) -> LasData:
        for proc in self.context.pipeline:
            las = proc(las)
        return las

    def manage_folders(self, input_paths, output_folder) -> None:
        # Managing input folder
        assert input_paths[0].exists()
        self.context.input_path = input_paths[0]

        # Managing output folder
        if self.context.input_path.is_file():
            self.context.input_folder = self.context.input_path.parent
            if not output_folder:
                self.context.output_folder = self.context.input_path.parent
        elif self.context.input_path.is_dir():
            self.context.input_folder = self.context.input_path
            if not output_folder:
                self.context.output_folder = self.context.input_path
        if output_folder:
            output_folder = Path(output_folder)
            assert output_folder.exists()
            self.context.output_folder = output_folder

    def run(self) -> None:
        if self.context.input_path.is_file():
            las_paths = [self.context.input_path]  
        elif self.context.input_path.is_dir():
            las_paths = [p for p in self.context.input_path.iterdir() if p.is_file() and p.suffix in ['.las', '.laz']]
        
        for i, path in enumerate(las_paths):
            startt = time.time()

            print(f"[{i+1}/{len(las_paths)}]")
            
            las = laspy.read(path)
            las = self.context.apply_pipeline(las)
            outlas_path = self.context.output_folder / (path.stem+self.context.output_suffix+path.suffix)
            print(f"Writting to {outlas_path}")
            las.write( outlas_path )

            print(f"-- Processing time: {timedelta(seconds=time.time()-startt)}")