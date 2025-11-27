"""
Contains functions for procesing the transcription texts.
"""

import soundfile
import os
import csv
from librosa import load
import textgrid
import re
import string
import unicodedata

transcription_tiers_map = {
    "tcc": r"^Asmjeeg$",
    "201": r"^ref",
    "IGS": r"Transcription"
}

DIR_PATH = '../../data/6_11_2025_tcc'
OUT_PATH = '../../data/6_11_2025_tcc_annotations'

def remove_in_brackets_annotations(text):
    without = re.sub(r"\s*\([^)]*\)", "", text)
    return without.strip()

def remove_dialog_annotations(text):
    without = re.sub(r"[0-9]+;-", "", text)
    return without.strip()

def remove_alternatives(text):
    return text.split(' / ')[0]

def remove_interpunction(text):
    PUNCT = r"\.\,\!\?\"\-\_\:"
    DIGITS = r"0-9"
    return re.sub(f"[{PUNCT}{DIGITS}]", "", text)

def remove_diacritics(text):
    normalized = unicodedata.normalize("NFD", text)
    without_marks = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return unicodedata.normalize("NFC", without_marks)

def process_text(text, f_remove_dialogs=True, f_remove_brackets=True, f_remove_alternatives=True, f_remove_interpunction=True, f_remove_diacretics=True, f_lower_case=True):
    if f_remove_dialogs:
        text = remove_dialog_annotations(text)
    if f_remove_brackets:
        text = remove_in_brackets_annotations(text)
    if f_remove_alternatives:
        text = remove_alternatives(text)
    if f_remove_interpunction:
        text = remove_interpunction(text)
    if f_remove_diacretics:
        text = remove_diacritics(text)
    if f_lower_case:
        text = text.lower()
    
    return text.strip()
    

def process(file_name, folder_path, out_f):
    tg = textgrid.TextGrid.fromFile(os.path.join(folder_path, file_name + '.TextGrid')) 
    tier_name_pattern = transcription_tiers_map[file_name[:3]]
    
    for tier in tg.tiers:
        if not re.match(tier_name_pattern, tier.name):
            continue

        non_empty_intervals = [interval for interval in tier.intervals if interval.mark.strip()]
        if not non_empty_intervals:
            print('THERE ARENT ANY NON EMPTY INTERVALS :(', folder_path, file_name)
            return 0
        
        rel_folder = os.path.relpath(folder_path, DIR_PATH)
        out_f.write(f"{rel_folder}/{file_name}\n")
        
        for interval in non_empty_intervals:
            text = interval.mark.strip()
            processed = process_text(text)
            if processed != text:
                print('_original:', text)
                print('processed:', processed)
            out_f.write(processed + "\n")
        
        out_f.write("\n")
        
        return 1 
    return 0
            

def main():
    os.makedirs(OUT_PATH, exist_ok=True)
    out_file_path = os.path.join(OUT_PATH, "annotations_processed_2.txt")

    directories = [d for d in os.listdir(DIR_PATH) if os.path.isdir(os.path.join(DIR_PATH, d))]

    with open(out_file_path, "w", encoding="utf-8") as out_f:
        for dir in directories:
            inner_path = os.path.join(DIR_PATH, dir)
            files = {file.split('.')[0] for file in os.listdir(inner_path) if file.endswith('.TextGrid')}
            
            for file in files:
                process(file, inner_path, out_f)


if __name__ == "__main__":
    main()
