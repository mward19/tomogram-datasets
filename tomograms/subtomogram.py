from .tomogram import Tomogram
from .annotation import Annotation

import numpy as np

from typing import List, Optional

def in_bounds(shape: np.ndarray, point: np.ndarray) -> bool:
    """ 
    Checks if the `point` is within the bounds of an array with the given
    `shape`.

    Args:
        shape (np.ndarray): The shape of the array. point (np.ndarray): The
        point to check.

    Returns:
        bool: True if the point is within bounds, False otherwise.
    """
    for (s, p) in zip(shape, point):
        if p < 0 or p >= s:
            return False
    return True

class Subtomogram(Tomogram):
    """ 
    A class representing a subtomogram extracted from a parent tomogram.

    Attributes:
        parent_tomogram (Tomogram): The tomogram from which this subtomogram was
        created.

        lower_bounds (np.ndarray): The lower bounds of the subtomogram as they
        would be indexed in the parent tomogram.

        data (np.ndarray): The 3D data of the subtomogram.

        shape (np.ndarray): The shape of the subtomogram.
    """

    def __init__(self, parent_tomogram: 'Tomogram', lower_bounds: np.ndarray, shape: np.ndarray) -> None:
        """ 
        Initializes a Subtomogram instance.

        Args:
            parent_tomogram (Tomogram): The parent tomogram.

            lower_bounds (np.ndarray): The lower bounds for the subtomogram.

            shape (np.ndarray): The shape of the subtomogram.
        """
        self.parent_tomogram = parent_tomogram
        self.lower_bounds = lower_bounds

        # Modify annotations from the parent tomogram to match this tomogram
        new_annotations: List[Annotation] = []
        for parent_annotation in self.parent_tomogram.annotations:
            new_points: List[np.ndarray] = []
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
    """ 
    A class for generating subtomograms from a parent tomogram.

    Attributes:
        tomogram (Tomogram): The parent tomogram to sample from.

        annotations (List[Annotation]): The annotations from the parent
        tomogram.

        vol_shape (Tuple[int, int, int]): The shape of the volumes to be
        generated.

        pads (Tuple[int, int, int]): The padding to apply to the boundaries.

        gen (np.random.Generator): Random number generator for sampling.
    """

    def __init__(self, tomogram: 'Tomogram') -> None:
        """ 
        Initializes a SubtomogramGenerator instance.

        Args:
            tomogram (Tomogram): The parent tomogram to sample from.
        """
        self.tomogram = tomogram
        self.tomogram.load()
        self.annotations = self.tomogram.annotations
        self.vol_shape = (64, 256, 256)
        self.pads = (8, 32, 32)
        self.gen = np.random.default_rng()

    def set_vol_shape(self, new_vol_shape: tuple[int, int, int]) -> None:
        """ 
        Sets a new volume shape for the generator.

        Args:
            new_vol_shape (tuple[int, int, int]): The new volume shape.
        """
        self.vol_shape = new_vol_shape

    def positive_sample(self, point: Optional[np.ndarray] = None) -> Subtomogram:
        """ 
        Returns a random subtomogram containing the specified point.

        The point will not be closer than `pads` voxels to the respective
        borders. If no point is given, a random annotation point from
        self.tomogram's annotations is selected.

        Args:
            point (Optional[np.ndarray]): The point to include in the
            subtomogram. Defaults to None.

        Returns:
            Subtomogram: The newly created subtomogram.
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
            for (ts, vs, pt, pad) in zip(self.tomogram.shape, self.vol_shape, point, self.pads)]
        
        lower_bounds = [self.gen.choice(lb, shuffle=False) for lb in possible_lower_bounds]

        # Construct a new Tomogram with modified annotations
        return Subtomogram(self.tomogram, lower_bounds, self.vol_shape)

    def negative_sample(self) -> Subtomogram:
        """ 
        Returns a random subtomogram that does not contain any points from the
        annotations.

        This process continues until a valid subtomogram is found or the maximum
        iterations are reached.

        Returns:
            Subtomogram: The newly created subtomogram.

        Raises:
            Exception: If unable to find a valid subtomogram without annotation
            points after 1000 attempts.
        """
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
    
    def find_annotation_points(self) -> List[np.ndarray]:
        """ 
        Returns a list of points that are present in the annotations.

        Returns:
            List[np.ndarray]: A list of annotation points.
        """
        points: List[np.ndarray] = []
        for annotation in self.annotations:
            points += annotation.points
        return points


if __name__ == "__main__":
    from supercomputer_utils import all_fm_tomograms
    from visualize_voxels import visualize

    tomos = all_fm_tomograms()
    tomo = tomos[0]
    stg = SubtomogramGenerator(tomo)
    samps = [stg.negative_sample() if i%2 == 1 else stg.positive_sample(tomo.annotations[0].points[0])
             for i in range(5)]
    for (index, neg_samp) in enumerate(samps):
        visualize(neg_samp.data, marks=neg_samp.annotation_points())

