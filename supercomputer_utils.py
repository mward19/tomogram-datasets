import re
import os
from annotation import AnnotationFile
from tomogram import TomogramFile

def seek_file(directory, regex):
    """ Looks for a file matching `regex` recursively in `directory`."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if regex.match(file):
                return os.path.join(root, file)
        for dir in dirs:
            target = seek_file(dir, regex)
            if target is not None:
                return target
    return None

def seek_dirs(root, regex, directories=None):
    """ Looks for directories recursively within `directory` to find those matching `regex`."""
    # Initialize directories
    if directories is None:
        directories = []
    for root, dirs, _ in os.walk(root):
        for dir in dirs:
            if regex.match(dir):
                directories.append(os.path.join(root, dir))
            else:
                directories = seek_dirs(dir, regex, directories)
    return directories

def seek_set(directory, regexes, matches=None):
    """ Recursively step into `directory` and seek exactly one match for each regex in `regexes`. TODO: If extra matches are found, log the directory and return None. """
    # Initialize `matches`
    if matches is None:
        matches = [None for r in regexes]

    for root, dirs, files in os.walk(directory):
        for file in files:
            for r_idx, r in enumerate(regexes):
                if re.match(r, file):
                    if matches[r_idx] is None:
                        matches[r_idx] = os.path.join(root, file)
                    else:
                        return None # Extra match found
    return matches

def seek_annotated_tomos(directories, tomo_regex, annotation_regexes, annotation_names):
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

def all_fm_tomograms():
    """
    Collects all pairs of `.rec` tomogram filepaths and flagellar motor `.mod`
    filepaths from the supercomputer. Returned as a list of 
    Tomogram objects (with annotations stored in the Tomograms).
    """
    tomograms = []
    
    # ~~~ DRIVE 1 ~~~ #
    # Hylemonella
    root = f"/grphome/grp_tomo_db1_d1/nobackup/archive/TomoDB1_d1/FlagellarMotor_P1/Hylemonella gracilis"

    dir_regex = re.compile(r"yc\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^fm.mod$", re.IGNORECASE)
    tomogram_regex = re.compile(r".*\.rec$")
    

    these_tomograms = seek_annotated_tomos(directories, tomogram_regex, [flagellum_regex], ["Flagellar Motor"])
    tomograms += these_tomograms

    # ~~~ DRIVE 2 ~~~ #
    # Legionella
    root = f"/grphome/grp_tomo_db1_d2/nobackup/archive/TomoDB1_d2/FlagellarMotor_P2/legionella"

    dir_regex = re.compile(r"dg\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^FM\.mod$")
    tomogram_regex = re.compile(r".*SIRT_1k\.rec$")
    

    these_tomograms = seek_annotated_tomos(directories, tomogram_regex, [flagellum_regex], ["Flagellar Motor"])
    tomograms += these_tomograms

    # Pseudomonas
    root = f"/grphome/grp_tomo_db1_d2/nobackup/archive/TomoDB1_d2/FlagellarMotor_P2/Pseudomonasaeruginosa/done"

    dir_regex = re.compile(r"ab\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^FM\.mod$")
    tomogram_regex = re.compile(r".*SIRT_1k\.rec$")
    

    these_tomograms = seek_annotated_tomos(directories, tomogram_regex, [flagellum_regex], ["Flagellar Motor"])
    tomograms += these_tomograms

    ## Thiomicrospira (has some issues it looks like)
    #root = f"/grphome/grp_tomo_db1_d2/nobackup/archive/TomoDB1_d2/FlagellarMotor_P2/Thiomicrospira_crunogena"
    #
    #dir_regex = re.compile(r"ci\d{4}.*")
    #directories = seek_dirs(root, dir_regex)
    #
    #flagellum_regex = re.compile(r"^FM\.mod$")
    #tomogram_regex = re.compile(r".*\.rec$")
    #
    #
    #these_tomograms = seek_annotated_tomos(directories, tomogram_regex, [flagellum_regex], ["Flagellar Motor"])
    #tomograms += these_tomograms

    # Proteus_mirabilis
    root = f"/grphome/grp_tomo_db1_d2/nobackup/archive/TomoDB1_d2/FlagellarMotor_P2/Proteus_mirabilis"

    dir_regex = re.compile(r"qya\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^FM\.mod$")
    tomogram_regex = re.compile(r".*\.rec$")
    

    these_tomograms = seek_annotated_tomos(directories, tomogram_regex, [flagellum_regex], ["Flagellar Motor"])
    tomograms += these_tomograms

    # ~~~ DRIVE 3 ~~~ #
    # Bdellovibrio
    root = f"/grphome/grp_tomo_db1_d3/nobackup/archive/TomoDB1_d3/jhome_extra/Bdellovibrio_YW"

    dir_regex = re.compile(r"yc\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^flagellum_SIRT_1k\.mod$")
    tomogram_regex = re.compile(r".*SIRT_1k\.rec$")
    

    these_tomograms = seek_annotated_tomos(directories, tomogram_regex, [flagellum_regex], ["Flagellar Motor"])
    tomograms += these_tomograms

    # Azospirillum
    root = f"/grphome/grp_tomo_db1_d3/nobackup/archive/TomoDB1_d3/jhome_extra/AzospirillumBrasilense/done"

    dir_regex = re.compile(r"ab\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^FM3\.mod$")
    tomogram_regex = re.compile(r".*SIRT_1k\.rec$")
    

    these_tomograms = seek_annotated_tomos(directories, tomogram_regex, [flagellum_regex], ["Flagellar Motor"])
    tomograms += these_tomograms

    # ~~~ ZHIPING ~~~ #
    root = f"/grphome/fslg_imagseg/nobackup/archive/zhiping_data/caulo_WT/"

    dir_regex = re.compile(r"rrb\d{4}.*")
    directories = seek_dirs(root, dir_regex)
    
    flagellum_regex = re.compile(r"^flagellum\.mod$")
    tomogram_regex = re.compile(r".*\.rec$")
    

    these_tomograms = seek_annotated_tomos(directories, tomogram_regex, [flagellum_regex], ["Flagellar Motor"])
    tomograms += these_tomograms
    
    return tomograms

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