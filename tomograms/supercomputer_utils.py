"""
A collection of utilities for use on BYU's supercomputer.
"""


import re
import os
from .annotation import AnnotationFile
from .tomogram import TomogramFile

from typing import List, Union, Optional

def all_fm_tomograms() -> List[TomogramFile]:
    """Collect all pairs of `.rec` tomogram filepaths and flagellar motor `.mod` filepaths.

    Returns:
        TomogramFile objects with their annotations.
    """
    tomograms = []
    
    # ~~~ DRIVE 1 ~~~ #
    # Hylemonella
    root = f"/grphome/grp_tomo_db1_d1/nobackup/archive/TomoDB1_d1/FlagellarMotor_P1/Hylemonella gracilis"
    dir_regex = re.compile(r"yc\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^fm.mod$", re.IGNORECASE)
    tomogram_regex = re.compile(r".*\.rec$")
    
    these_tomograms = seek_annotated_tomos(
        directories, 
        tomogram_regex, 
        [flagellum_regex], 
        ["Flagellar Motor"]
    )
    tomograms += these_tomograms

    # ~~~ DRIVE 2 ~~~ #
    # Legionella
    root = f"/grphome/grp_tomo_db1_d2/nobackup/archive/TomoDB1_d2/FlagellarMotor_P2/legionella"
    dir_regex = re.compile(r"dg\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^FM\.mod$")
    tomogram_regex = re.compile(r".*SIRT_1k\.rec$")
    
    these_tomograms = seek_annotated_tomos(
        directories, 
        tomogram_regex, 
        [flagellum_regex], 
        ["Flagellar Motor"]
    )
    tomograms += these_tomograms

    # Pseudomonas
    root = f"/grphome/grp_tomo_db1_d2/nobackup/archive/TomoDB1_d2/FlagellarMotor_P2/Pseudomonasaeruginosa/done"
    dir_regex = re.compile(r"ab\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^FM\.mod$")
    tomogram_regex = re.compile(r".*SIRT_1k\.rec$")
    
    these_tomograms = seek_annotated_tomos(
        directories, 
        tomogram_regex, 
        [flagellum_regex], 
        ["Flagellar Motor"]
    )
    tomograms += these_tomograms

    # Proteus_mirabilis
    root = f"/grphome/grp_tomo_db1_d2/nobackup/archive/TomoDB1_d2/FlagellarMotor_P2/Proteus_mirabilis"
    dir_regex = re.compile(r"qya\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^FM\.mod$")
    tomogram_regex = re.compile(r".*\.rec$")
    
    these_tomograms = seek_annotated_tomos(
        directories, 
        tomogram_regex, 
        [flagellum_regex], 
        ["Flagellar Motor"]
    )
    tomograms += these_tomograms

    # ~~~ DRIVE 3 ~~~ #
    # Bdellovibrio
    root = f"/grphome/grp_tomo_db1_d3/nobackup/archive/TomoDB1_d3/jhome_extra/Bdellovibrio_YW"
    dir_regex = re.compile(r"yc\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^flagellum_SIRT_1k\.mod$")
    tomogram_regex = re.compile(r".*SIRT_1k\.rec$")
    
    these_tomograms = seek_annotated_tomos(
        directories, 
        tomogram_regex, 
        [flagellum_regex], 
        ["Flagellar Motor"]
    )
    tomograms += these_tomograms

    # Azospirillum
    root = f"/grphome/grp_tomo_db1_d3/nobackup/archive/TomoDB1_d3/jhome_extra/AzospirillumBrasilense/done"
    dir_regex = re.compile(r"ab\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^FM3\.mod$")
    tomogram_regex = re.compile(r".*SIRT_1k\.rec$")
    
    these_tomograms = seek_annotated_tomos(
        directories, 
        tomogram_regex, 
        [flagellum_regex], 
        ["Flagellar Motor"]
    )
    tomograms += these_tomograms

    # ~~~ ZHIPING ~~~ #
    root = f"/grphome/fslg_imagseg/nobackup/archive/zhiping_data/caulo_WT/"
    dir_regex = re.compile(r"rrb\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^flagellum\.mod$")
    tomogram_regex = re.compile(r".*\.rec$")
    
    these_tomograms = seek_annotated_tomos(
        directories, 
        tomogram_regex, 
        [flagellum_regex], 
        ["Flagellar Motor"]
    )
    tomograms += these_tomograms
    
    return tomograms

def seek_file(directory: str, regex: List[re.Pattern]) -> Union[str, None]:
    """Search for a file matching the given regex recursively in the specified
    directory.

    Args:
        directory (str): The root directory to start the search. regex
        (re.Pattern): The regex pattern to match the filenames.

    Returns:
        The full path of the matching file, or None if no match is
        found.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if regex.match(file):
                return os.path.join(root, file)
        for dir in dirs:
            target = seek_file(dir, regex)
            if target is not None:
                return target
    return None

def seek_dirs(
            root: str, 
            regex: re.Pattern, 
            directories: Optional[List[str]] = None
        ) -> Union[List[str], None]:
    """Search for directories matching the given regex recursively within the
    specified root directory.

    Args:
        root (str): The root directory to start the search.

        regex (re.Pattern): The regex pattern to match the directory names.
        
        directories (list, optional): A list to accumulate matched directories.
        Should not be set in general usage, as this is used only for internal
        recursion. Defaults to None.

    Returns:
        A list of paths of matching directories.
    """
    if directories is None:
        directories = []
    for root, dirs, _ in os.walk(root):
        for dir in dirs:
            if regex.match(dir):
                directories.append(os.path.join(root, dir))
            else:
                directories = seek_dirs(dir, regex, directories)
    return directories

def seek_set(
            directory: str, 
            regexes: List[re.Pattern], 
            matches: List[str] = None
        ) -> Union[List[str], None]:
    """Recursively search the specified directory for exactly one match for each regex in the list.

    Args:
        directory (str): The directory to search.

        regexes (list of re.Pattern): A list of regex patterns to match filenames.

        matches (list, optional): A list to accumulate matches. Should not be
        set in general usage, as this is used only for internal recursion.
        Defaults to None.

    Returns:
        A list of matching file paths or None if extra matches are found.
    """
    if matches is None:
        matches = [None for _ in regexes]

    for root, dirs, files in os.walk(directory):
        for file in files:
            for r_idx, r in enumerate(regexes):
                if re.match(r, file):
                    if matches[r_idx] is None:
                        matches[r_idx] = os.path.join(root, file)
                    else:
                        return None  # Extra match found
    return matches

def seek_annotated_tomos(
            directories: List[str], 
            tomo_regex: re.Pattern, 
            annotation_regexes: List[re.Pattern], 
            annotation_names: List[str]
        ) -> List[TomogramFile]:
    """Collect pairs of tomogram files and their corresponding annotation files.

    Args:
        directories (list of str): List of directories to search for tomograms
        and annotations.
        
        tomo_regex (re.Pattern): The regex pattern to match tomogram filenames.
        
        annotation_regexes (list of re.Pattern): A list of regex patterns to
        match annotation filenames.
        
        annotation_names (list of str): A list of names for the annotations.

    Returns:
        TomogramFile objects with their corresponding
        annotations.
    """
    tomos = []
    for dir in directories:
        matches = seek_set(dir, [tomo_regex] + annotation_regexes)
        if matches is not None and None not in matches:
            tomogram_file = matches[0]
            annotation_files = matches[1:]
            annotations = []
            for (file, name) in zip(annotation_files, annotation_names):
                annotations.append(AnnotationFile(file, name))
            tomo = TomogramFile(tomogram_file, annotations, load=False)
            tomos.append(tomo)
    return tomos



if __name__ == "__main__":
    # Run this to see annotations
    tomos = all_fm_tomograms()
    for tomo in tomos:
        print(tomo.filepath)
        for annotation in tomo.annotations:
            print(annotation.filepath)
            print(annotation.name)
            for point in annotation.points:
                print(point)
        print()
