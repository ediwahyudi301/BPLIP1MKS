import requests
import pandas as pd
import io

def debug_search_data():
    url6 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1894372110"
    try:
        r6 = requests.get(url6)
        df6 = pd.read_csv(io.StringIO(r6.text), header=None)
        print(f"Total rows: {len(df6)}")
        for i, row in df6.iterrows():
            row_str = ' '.join(str(cell).upper() for cell in row)
            if "PEKERJAAN PERSIAPAN" in row_str or "LAND CLEARING" in row_str:
                print(f"Match found at Row {i}:")
                print(row.tolist())
                # Also print the row above it to see the numbering
                if i > 0:
                    print(f"Row {i-1}: {df6.iloc[i-1].tolist()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_search_data()
