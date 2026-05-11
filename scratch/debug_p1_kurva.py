import requests
import pandas as pd
import io

def debug_p1_kurva():
    url1 = "https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL1"
    try:
        r1 = requests.get(url1)
        df1 = pd.read_csv(io.StringIO(r1.text), header=None)
        print("Searching for Kurva S labels in Paket 1...")
        for i, row in df1.iterrows():
            row_joined = ' '.join(str(cell).upper() for cell in row)
            if "KOMULATIF" in row_joined:
                print(f"Row {i}: {row.tolist()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_p1_kurva()
