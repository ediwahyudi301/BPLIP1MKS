import requests
import pandas as pd
import io

def debug_p1():
    url1 = "https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL1"
    try:
        r1 = requests.get(url1)
        df1 = pd.read_csv(io.StringIO(r1.text), header=None)
        print("Paket 1 Rows 30-50:")
        for i in range(30, 51):
            print(f"Row {i}: {df1.iloc[i].tolist()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_p1()
