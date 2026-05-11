import requests
import pandas as pd
import io

def debug_paket8_bottom():
    url8 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1047753912"
    try:
        r8 = requests.get(url8)
        df8 = pd.read_csv(io.StringIO(r8.text), header=None)
        print("Paket 8 Rows 100 to 150 search for Bobot:")
        for i, row in df8.iterrows():
            row_joined = ' '.join(str(cell).upper() for cell in row)
            if "BOBOT RENCANA" in row_joined or "KOMULATIF" in row_joined:
                print(f"Row {i}: {row_joined[:150]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_paket8_bottom()
