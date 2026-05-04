import requests, pandas as pd, io

url = 'https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL5'

req = requests.get(url)
df = pd.read_csv(io.StringIO(req.text))

found = False
for index, row in df.iterrows():
    row_joined = ' '.join(str(cell).upper() for cell in row)
    if 'KEMAJUAN PROGRES MINGGU 1' in row_joined:
        found = True
        continue
    if found:
        no_val = str(row.iloc[1]).strip()
        uraian_val = str(row.iloc[2]).strip()
        if no_val == '1' and uraian_val == '2':
            print(f"Skipping Row {index} (Label Row)")
            continue
        if no_val.isdigit() or (len(no_val) == 1 and no_val.isalpha() and no_val.isupper()):
            print(f"Row {index} (No: {no_val}, Uraian: {uraian_val[:20]}...): Col 15={row.iloc[15]}")
        if index > 60: break
