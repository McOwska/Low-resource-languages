"""
Creates (and saves to a txt file) list of all directories containing non-empty annotated intervals together with summed duration of intervals.
Helper for subsets devision.
"""

import os
import re
import textgrid
import soundfile
import numpy as np

DIR_PATH = '../../../data/6_11_2025_tcc'
OUT_PATH = '../../../data/6_11_2025_tcc_cv'
OUT_TXT = os.path.join(OUT_PATH, 'durations_by_directory.txt')

transcription_tiers_map = {
    "tcc": r"^Asmjeeg$",
    "201": r"^ref",
    "IGS": r"Transcription"
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

def get_nonempty_asmjeeg_duration_for_file(file_name, folder_path):
    tg_path = os.path.join(folder_path, file_name + '.TextGrid')
    if not os.path.exists(tg_path):
        print("NO TEXTGRID FILE:", tg_path)
        return 0.0

    tg = textgrid.TextGrid.fromFile(tg_path)

    file_type = file_name[:3]
    if file_type not in transcription_tiers_map:
        print("UNKNOWN FILE TYPE:", file_name)
        return 0.0

    tier_name_pattern = transcription_tiers_map[file_type]

    audio, sr = load_audio_for_file(folder_path, file_name)
    if audio is None:
        return 0.0

    total_duration = 0.0

    for tier in tg.tiers:
        if not re.match(tier_name_pattern, tier.name):
            continue

        non_empty_intervals = [interval for interval in tier.intervals if interval.mark.strip()]
        if not non_empty_intervals:
            continue

        for interval in non_empty_intervals:
            start, end = interval.minTime, interval.maxTime

            start_sample = int(start * sr)
            end_sample = int(end * sr)
            audio_segment = audio[start_sample:end_sample]

            if len(audio_segment) == 0:
                print("EMPTY AUDIO SEGMENT:", file_name, start, end)
                continue

            seg_duration = len(audio_segment) / sr
            total_duration += seg_duration

        break
    print('total', total_duration)
    return total_duration

def main():
    os.makedirs(OUT_PATH, exist_ok=True)

    directories = [
        d for d in os.listdir(DIR_PATH)
        if os.path.isdir(os.path.join(DIR_PATH, d))
    ]

    with open(OUT_TXT, "w", encoding="utf-8") as out_f:
        for directory in sorted(directories):
            inner_path = os.path.join(DIR_PATH, directory)
            files = {
                os.path.splitext(f)[0]
                for f in os.listdir(inner_path)
                if f.endswith('.TextGrid')
            }

            dir_total_duration = 0.0

            for file_name in files:
                dir_total_duration += get_nonempty_asmjeeg_duration_for_file(
                    file_name, inner_path
                )

            out_f.write(f"{directory}\t{dir_total_duration:.3f}\n")

if __name__ == "__main__":
    main()
