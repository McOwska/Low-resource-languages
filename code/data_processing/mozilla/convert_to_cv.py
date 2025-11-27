import csv
import os
import argparse
from datasets import Dataset, Audio

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, required=True)
parser.add_argument("--out_dir", type=str, required=True)
args = parser.parse_args()

os.makedirs(args.out_dir, exist_ok=True)
clips_out = os.path.join(args.out_dir, "clips")
os.makedirs(clips_out, exist_ok=True)

rows = []
with open(args.input, encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for r in reader:
        if r["sentence"].strip():
            rows.append({
                "path": r["path"],
                "sentence": r["sentence"],
                "locale": r.get("locale") or "sw"
            })

ds = Dataset.from_list(rows)
ds = ds.cast_column("path", Audio(sampling_rate=16000))

print(ds)
ds.save_to_disk(args.out_dir)
