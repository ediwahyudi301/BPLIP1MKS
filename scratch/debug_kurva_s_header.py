import requests
import pandas as pd
import io

def debug_kurva_s_header():
    url6 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1894372110"
    try:
        r6 = requests.get(url6)
        df6 = pd.read_csv(io.StringIO(r6.text), header=None)
        print("Printing Row 35-45:")
        for i in range(35, 46):
            if i < len(df6):
                print(f"Row {i}: {df6.iloc[i].tolist()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_kurva_s_header()
