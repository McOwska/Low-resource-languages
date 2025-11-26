import unicodedata
import collections
import sys
import re


def remove_diacritics(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    without_marks = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return unicodedata.normalize("NFC", without_marks)


def iter_tokens(lines):
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "/" in line and " " not in line:
            continue
        for token in line.split():
            yield token


def analyze_file(path, out_path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    base_to_forms = collections.defaultdict(set)
    base_to_counts = collections.defaultdict(collections.Counter)

    for tok in iter_tokens(lines):
        base = remove_diacritics(tok)
        base_to_forms[base].add(tok)
        base_to_counts[base][tok] += 1

    ambiguous = {
        base: base_to_counts[base]
        for base, forms in base_to_forms.items()
        if len(forms) > 1
    }

    def total_count(item):
        _, counter = item
        return sum(counter.values())

    with open(out_path, "w", encoding="utf-8") as out:
        for base, counter in sorted(ambiguous.items(), key=total_count, reverse=True):
            total = sum(counter.values())
            out.write(f"BASE (no accents): {base}  |  total: {total}, variants: {len(counter)}\n")
            for form, cnt in counter.most_common():
                out.write(f"    {form}\t{cnt}\n")
            out.write("\n")

    print(f"[DONE] Results written to: {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python check_diacritics.py <annotations_file> <output_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    analyze_file(input_path, output_path)
