import requests, pandas as pd, io

url = 'https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL5'

try:
    req = requests.get(url)
    req.encoding = 'utf-8'
    df = pd.read_csv(io.StringIO(req.text))

    with open('scratch/inspect_sulsel5.txt', 'w', encoding='utf-8') as f:
        for i, row in df.iterrows():
            row_list = [str(c) for c in row]
            f.write("Row " + str(i) + ": " + str(row_list) + "\n")
            row_joined = ' '.join(row_list).upper()
            if 'MINGGU' in row_joined:
                f.write("  --> FOUND MINGGU AT ROW " + str(i) + ": " + row_joined + "\n")

    print("Inspection complete. Check scratch/inspect_sulsel5.txt")
except Exception as e:
    print("Error:", e)
