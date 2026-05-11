import requests
import pandas as pd
import io

def debug_full_row47():
    url6 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1894372110"
    try:
        r6 = requests.get(url6)
        df6 = pd.read_csv(io.StringIO(r6.text), header=None)
        print(f"Row 47: {df6.iloc[47].tolist()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_full_row47()
