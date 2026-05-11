import requests
import pandas as pd
import io

def debug_p1_full():
    url1 = "https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL1"
    try:
        r1 = requests.get(url1)
        df1 = pd.read_csv(io.StringIO(r1.text), header=None)
        print("Paket 1 Row 39 (Full Columns):")
        row = df1.iloc[39].tolist()
        for j, val in enumerate(row):
            print(f"Col {j}: {val}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_p1_full()
