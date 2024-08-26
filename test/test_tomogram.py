import pytest

import numpy as np

import tomograms

# Random number generator
gen = np.random.default_rng()


@pytest.fixture(params=[0, 1, 2])
def sample_tomo(request): 
    """ 
    Generates small random tomograms with a random number of annotations.
    
    Each annotation is titled with an index, and the point it contains is [1, 2, 3] times that same index.

    The tomogram is 50 x 100 x 200.
    """
    # Fetch the number of annotations
    n_annotations = request.param

    data = gen.random(size=(50, 100, 200))
    annotations = [
        tomograms.Annotation(
            [i * np.array([1, 2, 3])], 
            str(i)
        ) 
        for i in range(n_annotations)
    ]
    return tomograms.Tomogram(data, annotations)

def test_add_annotation(sample_tomo):
    n_anns = len(sample_tomo.annotations)
    sample_tomo.add_annotation(tomograms.Annotation(np.array([0, 1, 2]), "addition"))
    assert n_anns + 1 == len(sample_tomo.annotations)

def test_annotation_points(sample_tomo):
    n_anns = len(sample_tomo.annotations)
    if n_anns == 0:
        return
    # Get all points.
    all_points = sample_tomo.annotation_points()
    assert len(all_points) == n_anns

    # Random annotation index
    i = gen.choice(range(n_anns))
    assert np.allclose(
        sample_tomo.annotation_points(i),
        np.array([1, 2, 3]) * i
    )

def test_mrc_to_np():
    file_1 = "test/data/mba2011-04-12-1.mrc" # https://cryoetdataportal.czscience.com/runs/10132
    # TODO: Portal says it's 318x319x109. Why 318 319 switch?
    array_1 = tomograms.TomogramFile.mrc_to_np(file_1)
    assert isinstance(array_1, np.ndarray)
    assert np.allclose(array_1.shape, (109, 319, 318))

def test_process():
    file_1 = "test/data/mba2011-04-12-1.mrc" # https://cryoetdataportal.czscience.com/runs/10132
    tomo = tomograms.TomogramFile(file_1)
    
    # Alter some data to ensure that the processing does something
    tomo.data[2, 3, 4] = -3

    orig_data = tomo.data.copy()
    orig_shape = tomo.shape
    tomo.process()
    assert np.allclose(tomo.shape, orig_shape)
    assert not np.allclose(tomo.data, orig_data)

def test_reload():
    file_1 = "test/data/mba2011-04-12-1.mrc" # https://cryoetdataportal.czscience.com/runs/10132
    tomo = tomograms.TomogramFile(file_1)
    
    # Alter some data to ensure that the processing does something
    tomo.data[2, 3, 4] = -3
    tomo.process()

    processed_data = tomo.data.copy()

    tomo.reload()

    assert not np.allclose(tomo.data, processed_data)

def test_get_shape_from_annotations():
    # TODO. Need a small tomogram with annotation
    pass