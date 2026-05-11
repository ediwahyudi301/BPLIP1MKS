import requests
import pandas as pd
import io

def debug_kurva_values():
    url6 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1894372110"
    try:
        r6 = requests.get(url6)
        df6 = pd.read_csv(io.StringIO(r6.text), header=None)
        row47 = df6.iloc[47].tolist()
        print(f"Row 47 (KOMULATIF RENCANA MINGGUAN):")
        # Print only non-nan values
        vals = [v for v in row47 if str(v).lower() != 'nan']
        print(vals)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_kurva_values()
