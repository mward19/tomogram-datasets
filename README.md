# tomograms
I work in the BYU Biophysics research group, 
in which we spend much of our time working with 3-dimensional images of bacteria called tomograms. 
Researchers have spent a lot of time looking for structures in these tomograms, and save their findings in annotation files. 
This repository contains code that makes it easier to navigate the web of tomograms and annotations we have,
simplifying analysis and dataset creation.

These classes and scripts aim to simplify that process for us.
The classes
 - Tomogram (and its child class TomogramFile),
 - Annotation (and its child class AnnotationFile), and
 - Subtomogram

abstractify the data and simplify connections.

The class SubtomogramGenerator generates Subtomograms (sub-volumes within Tomograms) based on Annotation data linked to Tomograms,
and can generate both Subtomograms containing Annotations and Subtomograms not containing any annotations.
This may be very useful in creating our next competition.

# Installation
Install with pip:
```shell
pip install git+https://github.com/mward19/tomograms.git
```
