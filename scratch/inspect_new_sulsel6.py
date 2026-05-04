import pandas as pd
import requests
import io

base_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&sheet="

# Check PAKET_SULSEL6 with header=None to see all raw data
sheet = "PAKET_SULSEL6"
url = base_url + sheet
print(f"SHEET: {sheet} - ALL ROWS (raw, no header)")
req = requests.get(url)
df = pd.read_csv(io.StringIO(req.text), header=None)
print(f"Shape: {df.shape}")
for i, row in df.iterrows():
    vals = {j: str(v).strip() for j, v in enumerate(row) if str(v).strip() not in ('', 'nan')}
    if vals:
        print(f"  Row {i}: {vals}")
