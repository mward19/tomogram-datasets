# tomograms
In the BYU biophysics research group, we have run a couple Kaggle competitions local to BYU, and are working on our third, which will be global.
Our data, much of which is available at the [CryoET Data Portal](https://cryoetdataportal.czscience.com/), can be a little complex,
especially when creating competition datasets, since it is 3-dimensional and is often stored in unusual file formats.
In addition, some files are related to others in complex ways.

These classes and scripts aim to simplify that process for us.
The classes
 - Tomogram (and its child class TomogramFile),
 - Annotation (and its child class AnnotationFile), and
 - Subtomogram

abstractify the data and simplify connections.

The class SubtomogramGenerator generates Subtomograms (sub-volumes within Tomograms) based on Annotation data linked to Tomograms,
and can generate both Subtomograms containing Annotations and Subtomograms not containing any annotations.
This may be very useful in creating our next competition.
