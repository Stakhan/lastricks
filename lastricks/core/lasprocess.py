from enum import Enum
from laspy import LasData
from abc import ABC, abstractmethod

class LASProcessType(Enum):
    SingleInput = 1
    DoubleInput = 2
    MultipleInput = 3

class LASProcess(ABC):
    
    @abstractmethod    
    def __call__(self, *las: LasData) -> LasData:
        """Process a single python representation of a LAS/LAZ file.

        Args:
            *las (laspy.LasData): One or moreLAS/LAZ file representation
                to process.

        Returns:
            laspy.LasData: the resulting representation
        """
        pass
    
    def __str__(self):
        return f"{type(self).__name__}({self.__dict__})"
    
    @abstractmethod
    def get_type(self) -> LASProcessType:
        pass