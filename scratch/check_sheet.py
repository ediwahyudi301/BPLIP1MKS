import pandas as pd
import requests
import io
import sys

print("Python version:", sys.version)

URL = "https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL5"
req = requests.get(URL)
df = pd.read_csv(io.StringIO(req.text))
print("Total rows:", len(df))
print(df.iloc[-20:])
