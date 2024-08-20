import numpy as np
from skimage import exposure

import mrcfile

import os

from .annotation import Annotation
from .annotation import AnnotationFile

from typing import List, Optional

class Tomogram:
    """Represents a tomogram.

    Has fields for tomogram data and shape, as well as any annotations
    corresponding to the tomogram, which are represented with the Annotation
    class.

    Attributes:
        annotations (list of Annotation): Annotations corresponding to this
            tomogram.
        data (numpy.ndarray): A 3-dimensional array containing the
            tomogram image. 
        shape (numpy.ndarray): A 3-element array representing the shape of the
            tomogram data.
   
    """
    def __init__(self, data: np.ndarray, annotations: Optional[List[Annotation]] = None):
        """Initialize a Tomogram instance.

        Args:
            data (numpy.ndarray): A 3-dimensional array containing the tomogram image.
            annotations (list of Annotation, optional): A list of annotations
                corresponding to the tomogram. Defaults to None.
        """
        self.annotations = [] if annotations is None else annotations
        self.data = data
        self.shape = data.shape
    
    def add_annotation(self, annotation: Annotation):
        """Add an annotation to the tomogram.

        Args:
            annotation (Annotation): An annotation object to be added to
                the tomogram's annotations.
        """
        self.annotations.append(annotation)
    
    def annotation_points(self, annotation_index: Optional[int] = None):
        """Get annotation points from the tomogram.

        Retrieves annotation points from a specific annotation
        if an index is provided, or all annotation points from all
        annotations if no index is given.

        Args:
            annotation_index (int, optional): The index of the annotation
                from which to retrieve points. If None, retrieves points
                from all annotations. Defaults to None.

        Returns:
            list: A list of points from the specified annotation or
                all annotations.
        """
        if annotation_index is not None:
            return self.annotations[annotation_index].points
        else:
            indices = range(len(self.annotations))
            points = []
            for index in indices:
                points += self.annotation_points(index)
            return points
        


class TomogramFile(Tomogram):
    """Represents a tomogram file.

    Extends the Tomogram class to handle file operations, including loading
    tomogram data from files of specific formats.

    Attributes:
        filepath (str): The file path to the tomogram file. annotations (list of
        Annotation): Annotations corresponding to the
            tomogram.
        data (numpy.ndarray): A 3-dimensional array containing the tomogram
            image.
    """

    def __init__(
            self, 
            filepath: str, 
            annotations: 
            Optional[List[Annotation]] = None, 
            *, 
            load: bool = False
        ):
        """Initialize a TomogramFile instance.

        Args:
            filepath (str): The file path to the tomogram file.
            annotations (list of Annotation, optional): Annotations
                corresponding to the tomogram. Defaults to None.
            load (bool, optional): Whether to load tomogram array data
                immediately. Defaults to False.
        """
        if load:
            self.data = self.load()
        else:
            self.data = None
        self.annotations = annotations
        self.filepath = filepath

    def load(self, *, preprocess: bool = True):
        """Load the tomogram data from the specified file.

        This method determines the file type based on its extension and loads
        the data accordingly.

        Args:
            preprocess (bool, optional): Whether to preprocess the data after
                loading. Defaults to True.

        Returns:
            numpy.ndarray: The loaded tomogram data.

        Raises:
            IOError: If the file type is not supported.
        """
        if self.data is not None:
            return self.data
        
        # Determine how to load based on file extension.
        root, extension = os.path.splitext(self.filepath)
        if extension in [".mrc", ".rec"]:
            data = TomogramFile.mrc_to_np(self.filepath)
        elif extension == ".npy":
            data = np.load(self.filepath)
        else:
            raise IOError("Tomogram file must be of type .mrc, .rec, or .npy.")
        
        # Initialize Tomogram class
        super().__init__(data, self.annotations)

        if preprocess:
            self.process()
        
        return self.data

    @staticmethod
    def rescale(array: np.ndarray) -> np.ndarray:
        """Rescale array values to the range [0, 1].

        Args:
            array (numpy.ndarray): The array to be rescaled.

        Returns:
            numpy.ndarray: The rescaled array.
        """
        maximum = np.max(array)
        minimum = np.min(array)
        range_ = maximum - minimum
        return (array - minimum) / range_

    @staticmethod
    def mrc_to_np(filepath: str) -> np.ndarray:
        """Convert a .mrc or .rec file to a numpy array.

        Args:
            filepath (str): The file path to the .mrc or .rec file.

        Returns:
            numpy.ndarray: The data loaded as a numpy array.
        """
        with mrcfile.open(filepath, 'r') as mrc:
            data = mrc.data.astype(np.float64)
            return data

    def process(self):
        """Process the tomogram to improve contrast using contrast stretching.

        This method applies contrast stretching to enhance the visibility
        of features in the tomogram.
        
        Returns:
            numpy.ndarray: The processed tomogram data.
        """
        # Contrast stretching
        p2, p98 = np.percentile(self.data, (2, 98))
        data_rescale = exposure.rescale_intensity(self.data, in_range=(p2, p98))
        self.data = data_rescale
        return self.data

    def reload(self) -> np.ndarray:
        """Reload the tomogram data from the file.

        This method reinitializes the tomogram data by loading it again
        from the specified file.

        Returns:
            numpy.ndarray: The reloaded tomogram data.
        """
        self.data = TomogramFile.mrc_to_np(self.filepath)
        return self.data

    def get_shape_from_annotations(self):
        """
        Returns the shape of the tomogram without having to load it using the
        annotations attatched to this tomogram, if any are AnnotationFiles. If
        no AnnotationFiles are in self.annotations, raises an exception.

        Returns:
            numpy.ndarray: The shape of the tomogram as inferred from
            self.annotations.

        Raises:
            Exception: If no AnnotationFile objects are in self.annotations.

            Exception: If there are multiple AnnotationFile objects in
            self.annotations and they imply inconsistent shapes.
        """
        shapes = []
        for annotation in self.annotations:
            if isinstance(annotation, AnnotationFile):
                shape = annotation.tomogram_shape()
                shapes.append(shape)
    
        if len(shapes) == 0:
            raise Exception("No .mod annotations found. Cannot infer tomogram shape.")
        elif len(shapes) == 1:
            return shapes[0]
        else: # Confirm that all the shapes agree
            shape = shapes[0]
            for s in shapes[1:]:
                if s != shape:
                    raise Exception(f"Inconsistent tomogram shapes of {shape} and {s} implied by .mod annotations.")
            return shape

