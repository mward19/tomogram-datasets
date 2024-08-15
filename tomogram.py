import numpy as np
from skimage import exposure

import mrcfile

import os

from annotation import Annotation

class Tomogram:
    """
    Attributes:
        data
        shape
        processed (np array) Processed tomogram
        annotations (list of Annotations)
        file (str) filepath of this tomogram
    """
    def __init__(self, data, annotations=None):
        self.annotations = [] if annotations is None else annotations
        self.data = data
        self.shape = data.shape
    
    def add_annotation(self, annotation):
        self.annotations.append(annotation)
    
    def annotation_points(self, annotation_index=None):
        """ Get a list of all annotation points in the corresponding annotation, or if no annotation is provided, all annotation points in all annotations. """
        if annotation_index is not None:
            return self.annotations[annotation_index].points
        else:
            indices = range(len(self.annotations))
            points = []
            for index in indices:
                points += self.annotation_points(index)
            return points


class TomogramFile(Tomogram):
    def __init__(self, filepath, annotations=None, *, load=False):
        """
        Arguments:
        filepath (str) filepath of tomogram file.
        annotations (list of Annotation)
        load (bool) whether to load tomogram array data immediately or not.
        """
        if load:
            self.load()
        else:
            self.data = None
        self.annotations = annotations
        self.filepath = filepath
    
    def load(self, *, preprocess=True):
        """ Initializes Tomogram parent class. """
        if self.data is not None:
            return self.data
        # Determine how to load based on file extension.
        root, extension = os.path.splitext(self.filepath)
        if extension == ".mrc" or extension == ".rec":
            data = TomogramFile.mrc_to_np(self.filepath)
        elif extension == ".npy":
            data = np.load(self.filepath)
        else:
            raise IOError("Tomogram file must be of type .mrc, .rec, or .npy.")
        
        # Initialize Tomogram class
        super().__init__(data, self.annotations)

        if preprocess: self.process()
        
        return self.data

    def rescale(array):
        """ Rescales array values so that all values are between 0 and 1. """
        maximum = np.max(array)
        minimum = np.min(array)
        range = maximum - minimum
        return (array - minimum) / range
    
    def mrc_to_np(filepath):
        """ Converts .mrc file (or .rec file) to numpy array. """
        with mrcfile.open(filepath, 'r') as mrc:
            data = mrc.data.astype(np.float64)
            return data
    
    def process(self):
        """ Simple tomogram processing - uses contrast stretching to improve contrast. """
        # Contrast stretching
        p2, p98 = np.percentile(self.data, (2, 98))
        data_rescale = exposure.rescale_intensity(self.data, in_range=(p2, p98))
        self.data = data_rescale
        return self.data
    
    def reload(self):
        self.data = Tomogram.mrc_to_np(self.filepath)
        return self.data
    
    def mrc_shape(filepath):
        pass
        # TODO: use mrcfile.
        # mrc = mrcfile.open('tmp.mrc')
        # mrc.header
    
