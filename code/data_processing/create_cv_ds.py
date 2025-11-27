import annotations_processing
import os
import textgrid
import re
import soundfile
import csv
import numpy as np
import pandas as pd

DIR_PATH = '../../data/6_11_2025_tcc'
OUT_PATH = '../../data/6_11_2025_tcc_cv'
SPLITS_PATH = '../../data/6_11_2025_tcc_cv/splits'

transcription_tiers_map = {
    "tcc": r"^Asmjeeg$",
    "201": r"^ref",
    "IGS": r"Transcription"
}

eng_tiers_map = {
    "tcc": r"^English$",
    "201": r"^??",
    "IGS": r"??"
}

sw_tiers_map = {
    "tcc": r"^Swahili$",
    "201": r"^??",
    "IGS": r"??"
}

def load_audio_for_file(folder_path, file_name):
    exts = [".wav", ".flac", ".mp3", ".ogg"]
    audio_path = None
    for ext in exts:
        candidate = os.path.join(folder_path, file_name + ext)
        if os.path.exists(candidate):
            audio_path = candidate
            break

    if audio_path is None:
        print("NO AUDIO FILE FOUND FOR:", folder_path, file_name)
        return None, None

    audio, sr = soundfile.read(audio_path)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    return audio, sr

def _ensure_output_dir(output_path):
    clips_path = os.path.join(output_path, 'clips')
    os.makedirs(clips_path, exist_ok=True)

def _ensure_tsv_header(tsv_path):
    if not os.path.exists(tsv_path):
        with open(tsv_path, "w", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(["path","sentence","eng", "sw"])

def append_row(tsv_path, audio_path, sentence, eng, sw):
    with open(tsv_path, "a", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow([audio_path, sentence, eng, sw])

def save_segment(output_dir, segment_id, audio_file, sr, asmjeeg_str, eng_str, sw_str, subset):
    audio_path = os.path.join(output_dir, 'clips', segment_id + '.mp3')
    _ensure_output_dir(output_dir)
    soundfile.write(audio_path, audio_file, sr)

    tsv_path = os.path.join(output_dir, f'{subset}_dataset.tsv')
    _ensure_tsv_header(tsv_path)
    audio_relative_path = os.path.join('clips', segment_id + '.mp3')
    append_row(tsv_path, audio_relative_path, asmjeeg_str.strip(), eng_str.strip(), sw_str.strip())

def find_translations(tiers, interval, file_type):
    eng_name_pattern = eng_tiers_map[file_type]
    sw_name_pattern = sw_tiers_map[file_type]
    eng, sw = '', ''
    for tier in tiers:
        if re.match(eng_name_pattern, tier.name):
            for eng_interval in tier.intervals:
                if eng_interval.minTime == interval.minTime and eng_interval.maxTime == interval.maxTime:
                    eng = eng_interval.mark.strip()
        
        if re.match(sw_name_pattern, tier.name):
            for sw_interval in tier.intervals:
                if sw_interval.minTime == interval.minTime and sw_interval.maxTime == interval.maxTime:
                    sw = sw_interval.mark.strip()    
    return eng, sw

def process(file_name, folder_path, subset):
    tg = textgrid.TextGrid.fromFile(os.path.join(folder_path, file_name + '.TextGrid')) 
    tier_name_pattern = transcription_tiers_map[file_name[:3]]

    audio, sr = load_audio_for_file(folder_path, file_name)

    rel_folder = os.path.relpath(folder_path, DIR_PATH).replace(os.sep, "_")

    if audio is None:
        return 0

    for tier in tg.tiers:
        if not re.match(tier_name_pattern, tier.name):
            continue

        non_empty_intervals = [interval for interval in tier.intervals if interval.mark.strip()]
        if not non_empty_intervals:
            print('THERE ARENT ANY NON EMPTY INTERVALS :(', folder_path, file_name)
            return 0
        
        for interval in non_empty_intervals:
            text_raw = interval.mark.strip()
            try:
                asmjeeg_str = annotations_processing.process_text(text_raw)
            except AttributeError:
                asmjeeg_str = text_raw
            

            start, end = interval.minTime, interval.maxTime
            text_eng, text_sw = find_translations(tg.tiers, interval, file_name[:3])
            
            start_sample = int(start * sr)
            end_sample = int(end * sr)
            audio_segment = audio[start_sample:end_sample]

            if len(audio_segment) == 0:
                print("EMPTY AUDIO SEGMENT:", file_name, start, end)
                continue

            segment_id = f"{rel_folder}_{file_name}_{int(start * 1000):07d}_{int(end * 1000):07d}"
            save_segment(OUT_PATH, segment_id, audio_segment, sr, asmjeeg_str, text_eng, text_sw, subset)
        
        return 1 
    return 0

def get_directories(path):
    subsets = ['train', 'test', 'valid']
    dirs = []
    for subset in subsets:
        dirs_df = pd.read_csv(path + f'/{subset}_dirs.txt', sep='\t')
        dirs_df.columns = ['dirs']
        dirs.append(dirs_df['dirs'].tolist())
    
    return dirs


def main():
    os.makedirs(OUT_PATH, exist_ok=True)

    all_directories = get_directories(SPLITS_PATH)

    for subset, dir_list in zip(['train', 'test', 'valid'], all_directories):
        for dir in dir_list:
            inner_path = os.path.join(DIR_PATH, dir)
            files = {file.split('.')[0] for file in os.listdir(inner_path) if file.endswith('.TextGrid')}
            
            for file in files:
                process(file, inner_path, subset)


if __name__ == "__main__":
    main()
