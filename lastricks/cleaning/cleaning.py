import time
import laspy
from pathlib import Path
from datetime import timedelta


class Cleaner:
    """General structure for easy LAS/LAZ files cleaning from
       a sequence of `lastricks.cleaning.CleaningProcess`.
       Handles both a single file or a folder of files.
    """

    def __init__(
        self,
        input_path,
        cleaning_pipeline,
        output_folder=None,
        output_suffix=None,
        ):
        """
        Args:
            input_path (str or Path): file or directory of files to clean.
            cleaning_pipeline (list(lastricks.cleaning.CleaningProcess)): list
                of cleaning process 
            output_folder (str or Path, optional): Target destination for
                cleaning result. Defaults to None.
            output_suffix (str, optional): Suffix appended to result filename.
                Shouldn't contain any dots. Defaults to None.
        """
        input_path = Path(input_path)
        
        assert input_path.exists()
        self.input_path = input_path
        assert len(cleaning_pipeline) > 0 
        self.cleaning_pipeline = cleaning_pipeline
        print("Cleaner object created with following CleaningProcess:\n--> "+'\n--> '.join([str(cp) for cp in cleaning_pipeline])+'\n')

        # Managing output folder
        if not output_folder and input_path.is_file():
            self.output_folder = input_path.parent
            input_folder = input_path.parent
        elif not output_folder and input_path.is_dir():
            self.output_folder = input_path
            input_folder = input_path
        elif output_folder:
            output_folder = Path(output_folder)
            assert output_folder.exists()
            self.output_folder = output_folder
        print('compare', input_folder, '\n',self.output_folder)
        
        # Managing output suffix
        if not output_suffix and input_folder == output_folder:
            self.output_suffix =  "_cleaned"
        elif not output_suffix:
            self.output_suffix = ''
        elif output_suffix:
            assert '.' not in output_suffix
            self.output_suffix = output_suffix

    def apply_pipeline(self, las):
        """Apply each `CleaningProcess` to a LAS/LAZ representation.

        Args:
            las (laspy.LasData): LAS/LAZ representation on which
                pipeline will be applied

        Returns:
            laspy.LasData: LAS/LAZ representation with cleaning
                pipeline applied
        """
        for proc in self.cleaning_pipeline:
            las = proc(las)
        return las

    def clean(self):

        if self.input_path.is_file():
            las_paths = [self.input_path]  

        elif input_path.is_dir():
            las_paths = [p for p in las_path.iterdir() if p.is_file() and p.suffix in ['.las', '.laz']]
        
        for i,path in enumerate(las_paths):
            startt = time.time()

            print(f"[{i+1}/{len(las_paths)}]")
            
            las = laspy.read(path)
            las = self.apply_pipeline(las)
            print('output_suffix', self.output_suffix)
            outlas_path = self.output_folder / (path.stem+self.output_suffix+path.suffix)
            print(f"Writting to {outlas_path}")
            las.write( outlas_path )

            print(f"-- Processing time: {timedelta(seconds=time.time()-startt)}")


class CleaningProcess:
    
    def __call__(self, las):
        """Process a single python representation of a LAS/LAZ file.

        Args:
            las (laspy.LasData): LAS/LAZ file representation to process

        Returns:
            laspy.LasData: the resulting representation
        """
        raise NotImplementedError
    
    def __str__(self):
        return f"{type(self).__name__}({self.__dict__})" 