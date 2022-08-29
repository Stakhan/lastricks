import time
import laspy
from pathlib import Path
from datetime import timedelta


class LASProcessor:
    """General structure for easy LAS/LAZ files processing from
       a sequence of `lastricks.lasprocessor.LASProcess`.
       Handles both a single file or a folder of files.
    """

    def __init__(
        self,
        input_path,
        pipeline,
        output_folder=None,
        output_suffix=None,
        ):
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
        input_path = Path(input_path)
        
        assert input_path.exists()
        self.input_path = input_path
        assert len(pipeline) > 0 
        self.pipeline = pipeline
        print("LASProcessor object created with following LASProcess(es):\n--> "+'\n--> '.join([str(p) for p in pipeline])+'\n')

        # Managing output folder
        if input_path.is_file():
            self.input_folder = input_path.parent
            if not output_folder:
                self.output_folder = input_path.parent
        elif self.input_path.is_dir():
            self.input_folder = input_path
            if not output_folder:
                self.output_folder = input_path
        if output_folder:
            output_folder = Path(output_folder)
            assert output_folder.exists()
            self.output_folder = output_folder
            
        
        # Managing output suffix
        if not output_suffix and self.input_folder == self.output_folder:
            self.output_suffix =  "_processed"
        elif not output_suffix:
            self.output_suffix = ''
        elif output_suffix:
            assert '.' not in output_suffix
            self.output_suffix = output_suffix

    def apply_pipeline(self, las):
        """Apply each `LASProcess` to a LAS/LAZ representation.

        Args:
            las (laspy.LasData): LAS/LAZ representation on which
                pipeline will be applied

        Returns:
            laspy.LasData: LAS/LAZ representation with process
                pipeline applied
        """
        for proc in self.pipeline:
            las = proc(las)
        return las

    def run(self):

        if self.input_path.is_file():
            las_paths = [self.input_path]  
        elif self.input_path.is_dir():
            las_paths = [p for p in self.input_path.iterdir() if p.is_file() and p.suffix in ['.las', '.laz']]
        
        for i, path in enumerate(las_paths):
            startt = time.time()

            print(f"[{i+1}/{len(las_paths)}]")
            
            las = laspy.read(path)
            las = self.apply_pipeline(las)
            outlas_path = self.output_folder / (path.stem+self.output_suffix+path.suffix)
            print(f"Writting to {outlas_path}")
            las.write( outlas_path )

            print(f"-- Processing time: {timedelta(seconds=time.time()-startt)}")


class LASProcess:
    
    def __call__(self, *las):
        """Process a single python representation of a LAS/LAZ file.

        Args:
            *las tuple(laspy.LasData): One or moreLAS/LAZ file representation
                to process.

        Returns:
            laspy.LasData: the resulting representation
        """
        raise NotImplementedError
    
    def __str__(self):
        return f"{type(self).__name__}({self.__dict__})"