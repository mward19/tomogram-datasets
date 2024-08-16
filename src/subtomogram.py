from tomogram import Tomogram
from annotation import Annotation

import numpy as np

def in_bounds(shape, point):
    """ Checks if np array `point` would be in bounds of an array with shape `shape`. """
    for (s, p) in zip(shape, point):
        if p < 0 or p >= s:
            return False
    return True

class Subtomogram(Tomogram):
    """
    Attributes:
    parent_tomogram (Tomogram): the tomogram from whence this came
    lower_bounds (3-element numpy array): the lower bounds of the subtomogram as they
        would be indexed in parent_tomogram
    data (3D numpy array): The subtomogram data
    shape (3-element numpy array): The shape of the subtomogram
    """
    def __init__(self, parent_tomogram, lower_bounds, shape):
        self.parent_tomogram = parent_tomogram

        self.lower_bounds = lower_bounds

        # Modify annotations from parent tomogram to match this tomogram
        new_annotations = []
        for parent_annotation in self.parent_tomogram.annotations:
            new_points = []
            # Offset original points for this new subtomogram
            for point in parent_annotation.points:
                new_point = point - lower_bounds
                # Check if new_point is even in the new tomogram
                if in_bounds(shape, new_point):
                    new_points.append(new_point) 
                # Otherwise continue
            # Add the annotation only if there are points in it
            if len(new_points) > 0:
                new_annotations.append(Annotation(
                        new_points, 
                        parent_annotation.name
                ))
        
        # Get subvolume data using lower bounds and shape
        min_0, min_1, min_2 = lower_bounds
        shape_0, shape_1, shape_2 = shape
        new_data = parent_tomogram.data[
            min_0 : min_0 + shape_0,
            min_1 : min_1 + shape_1,
            min_2 : min_2 + shape_2
        ]
        
        # Initialize this new Tomogram
        super().__init__(new_data, new_annotations)
        

class SubtomogramGenerator:
    def __init__(self, tomogram):
        self.tomogram = tomogram
        self.tomogram.load()
        self.annotations = self.tomogram.annotations
        self.vol_shape = (64, 256, 256)
        self.pads = (8, 32, 32)
        self.gen = np.random.default_rng()

    def set_vol_shape(self, new_vol_shape):
        self.vol_shape = new_vol_shape

    def positive_sample(self, point=None):
        """ 
        Returns a random subtomogram containing the np array `point`. 
        
        The point will not be closer than `pads` voxels to the respective borders. 
        If no point is given, pick a random annotation point from self.tomogram's annotations. 
        
        Returns the new subtomogram.
        """
        if point is None:
            # Pick a random annotation point from self.tomogram's annotations
            annotation = self.gen.choice(self.annotations)
            point = self.gen.choice(annotation.points)

        possible_lower_bounds = [np.linspace(
                                        max(0, pt - vs + pad),
                                        min(ts - vs, pt - pad),
                                        endpoint=False,
                                        dtype=int
                                    )
            for (ts, vs, pt, pad) in zip(self.tomogram.shape, self.vol_shape, point, self.pads)] # TODO: clean up syntax
        
        lower_bounds = [self.gen.choice(lb, shuffle=False) for lb in possible_lower_bounds]

        # Construct a new Tomogram with modified annotations
        return Subtomogram(self.tomogram, lower_bounds, self.vol_shape)
    
    def negative_sample(self):
        """ Returns a random subtomogram not containing any points from self.tomogram.annotation_points(). Returns the new subtomogram. """
        # Generate completely random bounds until one has no annotations
        maxiter = 1000
        for iter in range(maxiter):
            possible_lower_bounds = [np.linspace(
                                            0,
                                            ts - vs,
                                            endpoint=False,
                                            dtype=int
                                        )
                            for (ts, vs) in zip(self.tomogram.shape, self.vol_shape)]
            
            lower_bounds = [self.gen.choice(lb, shuffle=False)
                                for lb in possible_lower_bounds]
            
            # Check if this volume contains any annotation points
            contains_annotation = False
            for point in self.tomogram.annotation_points():
                new_point = point - lower_bounds
                if in_bounds(self.vol_shape, new_point):
                    contains_annotation = True
                    break
                
            if not contains_annotation:
                return Subtomogram(self.tomogram, lower_bounds, self.vol_shape)
            
        raise Exception("Failed to find a volume without an annotation")
    
    def find_annotation_points(self):
        """ Returns a list of points that are in self.annotations. """
        points = []
        for annotation in self.annotations:
            points += annotation.points
        return points


if __name__ == "__main__":
    from supercomputer_utils import all_fm_tomograms
    from visualize_voxels import visualize

    tomos = all_fm_tomograms()
    stg = SubtomogramGenerator(tomos[0])
    neg_samps = [stg.negative_sample() for _ in range(3)]
    for neg_samp in neg_samps:
        visualize(neg_samp.data, marks=neg_samp.annotation_points())

