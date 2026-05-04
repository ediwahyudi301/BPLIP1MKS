import requests, pandas as pd, io

url = 'https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL5'

req = requests.get(url)
df = pd.read_csv(io.StringIO(req.text))

# Check Row 57 (Data Row 1 of Minggu 1)
row57 = df.iloc[57]
for i, val in enumerate(row57):
    print(f"Index {i}: {val}")
