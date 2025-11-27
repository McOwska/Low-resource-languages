"""
To get only the transcribed files (.mp3 + .TextGrid pairs) of a proper type.

TYPE - type of a file, the first 3 letters of a file name !works like that only for the Asmjeeg dataset!
DIR_PATH - directory where all the data is saved. Containes subdirectories with actual audio and trancription files
OUTPUT_PATH - path to the new directory. Structure of the output dir will be the same as the input
"""

import os
import shutil

DIR_PATH = '../../data/6_11_2025'
TYPE = 'tcc'
OUTPUT_PATH =  f'../../data/6_11_2025_{TYPE}'

os.makedirs(OUTPUT_PATH, exist_ok=True)


for item in os.listdir(DIR_PATH):
    src_dir = os.path.join(DIR_PATH, item)
    if not os.path.isdir(src_dir):
        continue

    contains_type = any(
        f.startswith(TYPE)
        for f in os.listdir(src_dir)
        if os.path.isfile(os.path.join(src_dir, f))
    )

    if contains_type:
        dest_dir = os.path.join(OUTPUT_PATH, item)
        os.makedirs(dest_dir, exist_ok=True)

        files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
        mp3s = {f[:-4] for f in files if f.endswith('.mp3') and f.startswith(TYPE)}
        textgrids = {f[:-9] for f in files if f.endswith('.TextGrid') and f.startswith(TYPE)}
        pairs = mp3s.intersection(textgrids)

        for base in pairs:
            for ext in ['.mp3', '.TextGrid']:
                src_file = os.path.join(src_dir, base + ext)
                dest_file = os.path.join(dest_dir, base + ext)
                if os.path.exists(src_file):
                    shutil.copy2(src_file, dest_file)
                    



