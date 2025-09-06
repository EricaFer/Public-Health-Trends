# scripts/pull_worldbank.py
import csv, io, json, time, pathlib, urllib.request

OUT_DIR = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INDICATORS = {
    "SP.DYN.LE00.IN": "life_expectancy_years",
    "SP.DYN.IMRT.IN": "infant_mortality_per_1000",
    "SH.XPD.CHEX.GD.ZS": "health_spend_gdp_pct",
    "SH.PRV.SMOK": "smoking_prevalence_pct"
}
START_YEAR, END_YEAR = 2000, 2024

def worldbank_api(indicator, page=1):
    url = (f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
           f"?date={START_YEAR}:{END_YEAR}&format=json&per_page=20000&page={page}")
    with urllib.request.urlopen(url) as r:
        return json.load(r)

def fetch_indicator(indicator):
    data = worldbank_api(indicator, page=1)
    meta, rows = data[0], data[1]
    # if pagination exists, WB uses multiple pages; usually page=1 large per_page is enough
    return [
        {
            "country_code": r["country"]["id"],
            "country_name": r["country"]["value"],
            "year": int(r["date"]),
            "indicator_code": indicator,
            "value": None if r["value"] is None else float(r["value"]),
        }
        for r in rows
        if r.get("country") and r.get("date") is not None
    ]

def write_csv(indicator, human_name, records):
    out = OUT_DIR / f"worldbank_{indicator}_{START_YEAR}_{END_YEAR}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "country_code","country_name","year","indicator_code","value"
        ])
        w.writeheader()
        w.writerows(sorted(records, key=lambda x: (x["country_code"], x["year"])))
    print(f"Wrote {out}")

def main():
    for code, name in INDICATORS.items():
        try:
            recs = fetch_indicator(code)
            write_csv(code, name, recs)
            time.sleep(0.5)  # be polite
        except Exception as e:
            print(f"Failed {code}: {e}")

if __name__ == "__main__":
    main()
