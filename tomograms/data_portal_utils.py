"""
A collection of utilities for use on the CryoET Data Portal, a project built by the Chan Zuckerberg Imaging Institute and the Chan Zuckerberg Initiative.
"""

import os
from pathlib import Path
import tempfile

import cryoet_data_portal as portal

def data_portal_fm_tomograms():
    # Instantiate a client, using the data portal GraphQL API by default
    client = portal.Client()

    # Select runs that contain flagellar motor annotations
    tvs_list = portal.TomogramVoxelSpacing.find(client, [portal.TomogramVoxelSpacing.annotations.object_name.ilike(r"%flagel%")])

    #for r in runs:
    #    print(len(r.tomogram_voxel_spacings))
    #    for tvs in r.tomogram_voxel_spacings:
    #        for a in tvs.annotations:
    #            print(a.object_name)
    #        for t in tvs.tomograms:
    #            print(t.name)
    #        print()

    for tvs in tvs_list:
        print(tvs.id)
        
    temp_dir = tempfile.gettempdir()
    tvs_list[0].download_everything(temp_dir)

if __name__ == "__main__":
    data_portal_fm_tomograms()

