import requests, pandas as pd, io

url = 'https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL5'

try:
    req = requests.get(url)
    req.encoding = 'utf-8'
    df = pd.read_csv(io.StringIO(req.text))

    print("Columns:", len(df.columns))
    row57 = df.iloc[57]
    for i, val in enumerate(row57):
        print(f"Index {i}: {val} (Type: {type(val)})")

except Exception as e:
    print("Error:", e)
