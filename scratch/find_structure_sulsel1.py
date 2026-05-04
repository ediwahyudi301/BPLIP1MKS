import requests, pandas as pd, io

url = 'https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL1'

req = requests.get(url)
df = pd.read_csv(io.StringIO(req.text))

found_minggu = False
# Search for any row that might be the table header
for index, row in df.iterrows():
    row_joined = ' '.join(str(cell).upper() for cell in row)
    if 'URAIAN' in row_joined or 'NO' in row_joined:
        print(f"\n--- Found Table Header at Row {index} ---")
        # Print next few rows
        for j in range(index, index + 20):
            if j < len(df):
                r = df.iloc[j]
                print(f"Row {j}: {list(r)}")
        break
