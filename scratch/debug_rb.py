import requests
import pandas as pd
import io

def debug_rencana_bobot():
    url6 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1894372110"
    try:
        r6 = requests.get(url6)
        df6 = pd.read_csv(io.StringIO(r6.text), header=None)
        print("Searching for RENCANA BOBOT in Paket 6...")
        for i, row in df6.iterrows():
            row_joined = ' '.join(str(cell).upper() for cell in row)
            if "RENCANA BOBOT" in row_joined:
                print(f"Row {i}: {row.tolist()}")
                # Also print the row 2 rows after
                if i+2 < len(df6):
                    print(f"Row {i+2}: {df6.iloc[i+2].tolist()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_rencana_bobot()
