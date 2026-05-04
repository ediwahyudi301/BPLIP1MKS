import requests, pandas as pd, io

url = 'https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL5'

req = requests.get(url)
df = pd.read_csv(io.StringIO(req.text))

found_minggu = False
for index, row in df.iterrows():
    row_joined = ' '.join(str(cell).upper() for cell in row)
    if 'KEMAJUAN PROGRES MINGGU' in row_joined:
        print(f"\n--- Found {row_joined.strip()} at Row {index} ---")
        found_minggu = True
        continue
    
    if found_minggu:
        no_val = str(row.iloc[1]).strip()
        if no_val == '1':
            print(f"Data Row {index}:")
            for i, val in enumerate(row):
                if str(val).strip() not in ['nan', '-', '', '0', '0.0', '0,00']:
                    print(f"  Col {i}: {val}")
        if 'TOTAL HARGA' in row_joined:
            found_minggu = False
