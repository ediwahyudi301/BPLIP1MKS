import requests
import pandas as pd
import io

def debug_kurva_s_labels():
    url6 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1894372110"
    try:
        r6 = requests.get(url6)
        df6 = pd.read_csv(io.StringIO(r6.text), header=None)
        print("Searching for Kurva S labels...")
        for i, row in df6.iterrows():
            row_joined = ' '.join(str(cell).upper() for cell in row)
            if "KOMULATIF" in row_joined or "RENCANA" in row_joined or "REALISASI" in row_joined:
                if i < 20 or i > 100: # Skip the master summary part if it's there
                    print(f"Row {i}: {row_joined[:100]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_kurva_s_labels()
