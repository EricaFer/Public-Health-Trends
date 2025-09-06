# scripts/validate_tidy.py
import csv, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated" / "indicator_values_2000_2024.csv"

START_YEAR, END_YEAR = 2000, 2024

def main():
    seen = set()
    counts = collections.Counter()
    total = 0
    bad_years = 0
    null_values = 0

    with CURATED.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            total += 1
            key = (row["country_code"], row["indicator_code"], row["year"])
            if key in seen:
                counts["dupe"] += 1
            seen.add(key)

            y = int(row["year"])
            if y < START_YEAR or y > END_YEAR:
                bad_years += 1

            if row["value"] in ("", "None", None):
                null_values += 1

    print(f"Rows: {total}")
    print(f"Duplicates: {counts['dupe']}")
    print(f"Rows with out of range year: {bad_years}")
    print(f"Rows with null value: {null_values}")

    assert counts["dupe"] == 0, "Found duplicate (country, indicator, year)"
    assert bad_years == 0, "Found out of range years"
    print("Validation passed")

if __name__ == "__main__":
    main()
