"""Extract MCQs from chapter markdown into data/mcq_master.csv and flag duplicates."""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
Q_RE = re.compile(r"^\*\*([A-Z]\d?-\d{2,3})\.\*\*\s*(.+)$")
OPT_RE = re.compile(r"\(A\)\s*(.+?)\s*\(B\)\s*(.+?)\s*\(C\)\s*(.+?)\s*\(D\)\s*(.+)$")
ANS_RE = re.compile(r"^\*\*उत्तर:\s*([ABCD])\*\*\s*(.*)$")
REF_RE = re.compile(r"\*\((E\d{3})\)\*")


def parse(path, month_code):
    rows, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = Q_RE.match(line)
        if m:
            cur = {"MCQ_ID": m.group(1), "Question_Hindi": m.group(2).strip(), "A": "", "B": "", "C": "", "D": ""}
            continue
        if cur is None:
            continue
        o = OPT_RE.search(line)
        if o and not cur["A"]:
            cur["A"], cur["B"], cur["C"], cur["D"] = (x.strip() for x in o.groups())
            continue
        a = ANS_RE.match(line)
        if a:
            expl = a.group(2).lstrip("— ").strip()
            ref = REF_RE.search(expl)
            cur["Answer"] = a.group(1)
            cur["Explanation"] = REF_RE.sub("", expl).strip(" —")
            cur["Event_ID"] = f"2026-{month_code}-{ref.group(1)}" if ref else ""
            cur["QC_Check"] = "Pass" if cur["A"] else "Check-options"
            rows.append(cur)
            cur = None
        elif line.strip() and not line.startswith("|---") and cur["A"] == "":
            cur["Question_Hindi"] += " " + line.strip()
    return rows


def main():
    chapters = sorted((ROOT / "chapters").glob("*.md"))
    rows = []
    for ch in chapters:
        month_code = ch.name.split("_")[0]
        rows.extend(parse(ch, month_code))
    seen, dups = {}, []
    for r in rows:
        key = re.sub(r"\s+", "", r["Question_Hindi"])
        if key in seen:
            dups.append((seen[key], r["MCQ_ID"]))
            r["QC_Check"] = f"Duplicate-of:{seen[key]}"
        seen.setdefault(key, r["MCQ_ID"])
    fields = ["MCQ_ID", "Event_ID", "Question_Hindi", "A", "B", "C", "D", "Answer", "Explanation", "QC_Check"]
    out = ROOT / "data" / "mcq_master.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} MCQs written to {out}; duplicates: {dups or 'none'}")
    return 1 if dups else 0


if __name__ == "__main__":
    sys.exit(main())
