import pytest

import numpy as np
import pandas as pd

import tomograms

FILE_1 = "test/data/test_1.ndjson"
FILE_2 = "test/data/test_2.mod"

def test_check_ext():
    fake_file_1 = "testing/file/path/with/a/mod/file/test.mod"
    
    # Should not raise an exception
    tomograms.AnnotationFile.check_ext(fake_file_1, ".mod")
    
    with pytest.raises(IOError, match="Annotation must be a .ndjson file."):
        tomograms.AnnotationFile.check_ext(fake_file_1, ".ndjson")

    fake_file_2 = "j.ndjson"
    
    # Should not raise an exception
    tomograms.AnnotationFile.check_ext(fake_file_2, ".ndjson")
    
    with pytest.raises(IOError, match="Annotation must be a .mod file."):
        tomograms.AnnotationFile.check_ext(fake_file_2, ".mod")
def test_mod_to_pd():
    df = tomograms.AnnotationFile.mod_to_pd(FILE_2)
    assert isinstance(df, pd.DataFrame)

def test_mod_points():
    points = tomograms.AnnotationFile.mod_points(FILE_2)
    assert isinstance(points, list) 
    # TODO: actually read .mod in imod and investigate points

def test_ndjson_points():
    points = tomograms.AnnotationFile.ndjson_points(FILE_1)
    assert isinstance(points, list) 
    assert len(points) == 2
    # Ensure Z is put first
    assert np.allclose(points[0], np.array([120., 100., 110.]))
    assert np.allclose(points[1], np.array([220., 200., 210.]))

def test_tomogram_shape_from_mod():
    annotation = tomograms.AnnotationFile(FILE_2)
    shape = annotation.tomogram_shape_from_mod()
    assert len(shape) == 3
    # TODO: actually read .mod in imod and investigate shape