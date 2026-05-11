import requests
import pandas as pd
import io

def inspect_sheets():
    # URL for Paket Sulsel 5 (Old Link)
    url5 = "https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL5"
    # URL for Paket Sulsel 6 (New Link)
    url6 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&sheet=PAKET_SULSEL6"

    print("--- PAKET SULSEL 5 ---")
    try:
        r5 = requests.get(url5)
        df5 = pd.read_csv(io.StringIO(r5.text), header=None)
        # Display rows where information might be (Satuan Kerja, Pekerjaan, etc.)
        for i, row in df5.head(30).iterrows():
            print(f"Row {i}: {row.tolist()}")
    except Exception as e:
        print(f"Error fetching 5: {e}")

    print("\n--- PAKET SULSEL 6 ---")
    try:
        r6 = requests.get(url6)
        df6 = pd.read_csv(io.StringIO(r6.text), header=None)
        for i, row in df6.head(40).iterrows():
            print(f"Row {i}: {row.tolist()}")
    except Exception as e:
        print(f"Error fetching 6: {e}")

if __name__ == "__main__":
    inspect_sheets()
