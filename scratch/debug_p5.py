import requests
import pandas as pd
import io

def debug_paket5_values():
    # URL for Paket Sulsel 5 (Old Link)
    url5 = "https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL5"
    try:
        r5 = requests.get(url5)
        df5 = pd.read_csv(io.StringIO(r5.text), header=None)
        print("Searching for KOMULATIF RENCANA in Paket 5...")
        for i, row in df5.iterrows():
            row_joined = ' '.join(str(cell).upper() for cell in row)
            if "KOMULATIF RENCANA" in row_joined:
                vals = [v for v in row.tolist() if str(v).lower() != 'nan']
                print(f"Row {i}: {vals}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_paket5_values()
