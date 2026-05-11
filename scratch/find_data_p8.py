import requests
import pandas as pd
import io

def find_data_rows():
    url8 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1047753912"
    try:
        r8 = requests.get(url8)
        df8 = pd.read_csv(io.StringIO(r8.text), header=None)
        print("Rows with more than 10 numbers:")
        for i, row in df8.iterrows():
            nums = []
            for val in row:
                try:
                    cleaned = str(val).replace(',', '.').replace(' ', '').strip()
                    if cleaned and cleaned != 'nan':
                        float(cleaned)
                        nums.append(val)
                except: pass
            if len(nums) > 10:
                print(f"Row {i}: {row.tolist()[:30]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_data_rows()
