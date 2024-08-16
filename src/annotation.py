import imodmodel
import pandas as pd
import numpy as np

from imodmodel import ImodModel

class Annotation:
    def __init__(self, points, name=None):
        self.points = points
        self.name = "" if name is None else name

class AnnotationFile(Annotation):
    def __init__(self, filepath, name=None):
        self.filepath = filepath
        points = AnnotationFile.mod_points(filepath)
        super().__init__(points, name)
    
    def mod_to_pd(filepath):
        return imodmodel.read(filepath)

    def mod_points(filepath):
        # TODO: make this use ImodModel instead of pandas for speeeeeeeed
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
    
    def mod_shape(mod_path):
        model = ImodModel.from_file(mod_path)