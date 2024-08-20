import imodmodel
import pandas as pd
import numpy as np

import os 

from imodmodel import ImodModel

from typing import List, Optional

class Annotation:
    """Represents a tomogram annotation.

    Attributes:
        points (list of numpy.ndarray): Annnotation points
        name (str): Name of this annotation
    """
    def __init__(self, points: List[np.ndarray], name: Optional[str] = None):
        self.points = points
        self.name = "" if name is None else name

class AnnotationFile(Annotation):
    """Represents a .mod file.
    
    Extends the Annotation class to handle file operations, especially for .mod
    files.

    Attributes:
        filepath (str): Filepath of this annotation file
        df (pandas.DataFrame): DataFrame of this file
    """
    def __init__(self, filepath: str, name: Optional[str] = None):
        """Initializes an AnnotationFile with a .mod file.

        Args:
            filepath (str): The filepath of the annotation to load
            name (str): The name of this annotation

        Raises:
            IOError: If the file extension is not .mod.
        """
        AnnotationFile.check_mod(filepath)

        self.filepath = filepath
        self.df = AnnotationFile.mod_to_pd(self.filepath)

        points = AnnotationFile.mod_points(self.filepath)
        super().__init__(points, name)
    
    @staticmethod
    def mod_to_pd(filepath: str) -> pd.DataFrame:
        """Converts a .mod file to a pandas DataFrame.

        Args:
            filepath (str): File to convert

        Returns:
            pandas.DataFrame: DataFrame of the annotation file.

        Raises:
            IOError: If the file extension is not .mod.
        """
        AnnotationFile.check_mod(filepath)
        return imodmodel.read(filepath)
    
    @staticmethod
    def check_mod(filepath: str):
        """Ensures that a filepath is of .mod type.

        Args:
            filepath (str): Filepath to check.

        Raises:
            IOError: If the file extension is not .mod.
        """
        _, extension = os.path.splitext(filepath)
        if extension != ".mod":
            raise IOError("Annotation must be a .mod file.")

    @staticmethod
    def mod_points(filepath: str) -> List[np.ndarray]:
        """Reads a .mod file and extracts the points it contains.

        Args:
            filepath (str)
        
        Returns:
            list of numpy.ndarray: List of points in the annotation file.
        """
        df = AnnotationFile.mod_to_pd(filepath)
        points = []
        for _, row in df.iterrows():
            # Assumes point is 3D
            dim_labels = ['x', 'y', 'z']
            point = np.array([row[dim] for dim in dim_labels])
            # The annotations seem to have been stored with this indexing. 
            dims_order = [2, 1, 0] 
            points.append(point[dims_order])
        return points
    
    def tomogram_shape(self):
        """Finds the shape of the parent tomogram of this annotation.
        
        Returns:
        numpy.ndarray: Shape of the parent tomogram.
        """
        header = ImodModel.from_file(self.filepath).header
        return np.array([header.zmax, header.xmax, header.ymax])

    # TODO
    def mod_shape(mod_path):
        # model = ImodModel.from_file(mod_path)
        pass

    