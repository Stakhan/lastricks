import laspy
from pathlib import Path
from laspy import LasData

class InputManager:
    def __init__(self, input_path: Path) -> None:
        self.input_path = Path(input_path)
        assert self.input_path.exists()
        self.las_paths = self.get_las_paths()
    
    def get_las_paths(self) -> list:
        if self.input_path.is_file():
           return [ self.input_path ]  
        elif self.input_path.is_dir():
            return [
                p for p in self.input_path.iterdir()
                if p.is_file() and p.suffix in ['.las', '.laz']
                ]

    def query_las_path(self, query_path: Path) -> Path:
        assert query_path.is_file()
        results = [
            p for p in self.las_paths
            if query_path.stem in p.stem
            or p.stem in query_path.stem
            ]
        if len(results) == 0:
            raise FileNotFoundError(
                f"Couldn't find any LAS file matching {query_path.stem} in {self.input_path}"
                )
        elif len(results) == 1:
            return results[0]
        else:
            raise Exception(
                f"Looking for {query_path.stem} in '{p.parent}' but found"
                f"several matches: {[r.stem for r in results]}") 
    
    def query_las(self, query_path: Path) -> LasData:
        return laspy.read(
            self.query_las_path( query_path )
        )

    def directory(self):
        if self.input_path.is_dir():
            return self.input_path
        elif self.input_path.is_file():
            return self.input_path.parent

    def __len__(self):
        return len(self.las_paths)

    def __iter__(self):
        return iter(self.las_paths)