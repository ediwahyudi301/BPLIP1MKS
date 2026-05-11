import requests
import pandas as pd
import io

def debug_top_rows():
    url6 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1894372110"
    try:
        r6 = requests.get(url6)
        df6 = pd.read_csv(io.StringIO(r6.text), header=None)
        print("Rows with data (First 100):")
        for i, row in df6.head(100).iterrows():
            non_nan = [str(c) for c in row if str(c).lower() != 'nan' and str(c).strip() != '']
            if len(non_nan) > 3:
                print(f"Row {i}: {non_nan}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_top_rows()
