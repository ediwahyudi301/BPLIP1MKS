import requests
import pandas as pd
import io

def debug_kurva_s_labels_all():
    url6 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1894372110"
    try:
        r6 = requests.get(url6)
        df6 = pd.read_csv(io.StringIO(r6.text), header=None)
        print("Rows 0-100 search for week numbers:")
        for i, row in df6.head(100).iterrows():
            nums = []
            for val in row:
                try:
                    cleaned = str(val).replace(',', '.').replace(' ', '').strip()
                    if cleaned.isdigit() and int(cleaned) < 50:
                        nums.append(int(cleaned))
                except: pass
            if len(nums) > 10: # Probably the week numbers
                print(f"Row {i} looks like weeks: {row.tolist()[:30]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_kurva_s_labels_all()
