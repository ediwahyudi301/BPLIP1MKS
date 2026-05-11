import requests
import pandas as pd
import io

def debug_paket6():
    url6 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&sheet=PAKET_SULSEL6"
    try:
        r6 = requests.get(url6)
        df6 = pd.read_csv(io.StringIO(r6.text), header=None)
        print(f"Total rows: {len(df6)}")
        print("First 20 rows:")
        for i in range(min(20, len(df6))):
            print(f"Row {i}: {df6.iloc[i].tolist()[:10]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_paket6()
