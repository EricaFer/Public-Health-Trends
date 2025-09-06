# scripts/combine_to_tidy.py
import csv, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "curated"
OUT.mkdir(parents=True, exist_ok=True)

# picks up the files you created in Step 1
PATTERN = re.compile(r"worldbank_(?P<indicator>[^_]+)_(?P<start>\d{4})_(?P<end>\d{4})\.csv")

def read_csv(p):
    with p.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            yield {
                "country_code": row["country_code"],
                "country_name": row["country_name"],
                "year": int(row["year"]),
                "indicator_code": row["indicator_code"],
                "value": None if row["value"] in ("", "None", None) else float(row["value"]),
                "source": "world_bank"
            }

def main():
    rows = []
    for p in RAW.glob("worldbank_*.csv"):
        if not PATTERN.match(p.name):
            continue
        rows.extend(read_csv(p))

    rows.sort(key=lambda r: (r["country_code"], r["indicator_code"], r["year"]))
    out_path = OUT / "indicator_values_2000_2024.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "country_code","country_name","year","indicator_code","value","source"
        ])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out_path} with {len(rows)} rows")

if __name__ == "__main__":
    main()
