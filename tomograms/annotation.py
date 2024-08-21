"""
This module provides classes to work with tomogram annotations.
"""

import imodmodel
import pandas as pd
import numpy as np

import json

import os 

from imodmodel import ImodModel

from typing import List, Optional

class Annotation:
    """This class represents a tomogram annotation.

    Attributes:
        points (list of numpy.ndarray): Annnotation points
        name (str): Name of this annotation
    """
    def __init__(self, points: List[np.ndarray], name: Optional[str] = None):
        self.points = points
        self.name = "" if name is None else name

class AnnotationFile(Annotation):
    """This class represents an annotation file.
    
    Extends the Annotation class to handle file operations, especially for .mod
    files.

    Attributes:
        filepath (str): Filepath of this annotation file
        extension (str): File extension of this annotation file
        df (pandas.DataFrame): DataFrame of this file
    """
    def __init__(self, filepath: str, name: Optional[str] = None):
        """Initializes an AnnotationFile with a .mod file.

        Args:
            filepath (str): The filepath of the annotation to load
            name (str): The name of this annotation

        Raises:
            IOError: If the file extension is not .mod or .ndjson.
        """
        self.filepath = filepath
        _, extension = os.path.splitext(filepath)
        self.extension = extension

        if self.extension == ".mod":
            points = AnnotationFile.mod_points(self.filepath)
        elif self.extension == ".ndjson":
            points = AnnotationFile.ndjson_points(self.filepath)

        super().__init__(points, name)

    @staticmethod
    def check_ext(filepath: str, ext: str):
        """Ensures that filepath is of a given type.

        Args:
            filepath (str): The file to check.
            ext (str): The desired file extension, i.e., ".mod".

        Raises:
            IOError: If the file extension is not `ext`.
        """
        _, extension = os.path.splitext(filepath)
        if extension != ext:
            raise IOError(f"Annotation must be a {ext} file.")
    
    @staticmethod
    def mod_to_pd(filepath: str) -> pd.DataFrame:
        """Converts a .mod file to a pandas DataFrame.

        Args:
            filepath (str): File to convert

        Returns:
            DataFrame of the annotation file.

        Raises:
            IOError: If the file extension is not .mod.
        """
        AnnotationFile.check_ext(filepath, ".mod")
        return imodmodel.read(filepath)

    @staticmethod
    def mod_points(filepath: str) -> List[np.ndarray]:
        """Reads a .mod file and extracts the points it contains.

        Args:
            filepath (str)
        
        Returns:
            List of points in the annotation file.
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
    
    @staticmethod
    def ndjson_points(filepath: str) -> List[np.ndarray]:
        """Reads a .ndjson annotation file as stored on the CryoET Data Portal
        and extracts the points it contains.

        Args:
            filepath (str)

        Returns:
            List of points in the annotation file.
        """
        points = []

        with open(filepath, 'r') as file:
            for line in file:
                data = json.loads(line)
                if data.get("type") == "orientedPoint":
                    location = data.get("location")
                    if location:
                        point = np.array([location["z"], location["x"], location["y"]])
                        points.append(point)       
        return points
    
    def tomogram_shape_from_mod(self):
        """
        Finds the shape of the parent tomogram of this annotation, if this
        annotation is a `.mod` file.
        
        Returns:
            Shape of the parent tomogram.

        Raises:
            IOError: If this annotation is not a .mod file.
        """
        AnnotationFile.check_ext(self.filepath, ".mod")
        header = ImodModel.from_file(self.filepath).header
        return np.array([header.zmax, header.xmax, header.ymax])

    