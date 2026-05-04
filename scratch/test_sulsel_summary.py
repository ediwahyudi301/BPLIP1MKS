import pandas as pd
import requests
import io

old_url = 'https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=MASTER_PAKET_SULSEL'
new_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&sheet=MASTER_PAKET_SULSEL'

summary = {'target': 0.0, 'kontrak': 0.0, 'realized': 0.0, 'active': 0}

def clean_num(s):
    s = str(s).replace('Rp', '').strip()
    if not s or s.lower() == 'nan' or s == '-':
        return None
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except:
        return None

def process(df, min_no, max_no, col_luas, col_kontrak, col_real, skip=3):
    for i, row in df.iterrows():
        if i < skip:
            continue
        no_str = str(row.iloc[1]).strip()
        if no_str.lower() != 'nan':
            try:
                pkg = int(float(no_str))
                if min_no <= pkg <= max_no:
                    luas = clean_num(row.iloc[col_luas] if len(row) > col_luas else None)
                    kontrak = clean_num(row.iloc[col_kontrak] if len(row) > col_kontrak else None)
                    real = clean_num(row.iloc[col_real] if len(row) > col_real else None)
                    
                    print(f"  Paket {pkg}: Luas={luas}, Kontrak={kontrak}, Realisasi={real}")
                    
                    if luas: summary['target'] += luas
                    if kontrak: summary['kontrak'] += kontrak
                    if real: summary['realized'] += real
                    summary['active'] += 1
            except:
                pass

print("=== PAKET 1-5 (Old URL) ===")
df1 = pd.read_csv(io.StringIO(requests.get(old_url).text), header=None)
process(df1, 1, 5, col_luas=10, col_kontrak=9, col_real=12, skip=3)

print("\n=== PAKET 6-24 (New URL) ===")
df2 = pd.read_csv(io.StringIO(requests.get(new_url).text), header=None)
process(df2, 6, 24, col_luas=7, col_kontrak=6, col_real=9, skip=8)

print("\n=== TOTAL SUMMARY ===")
print(f"TARGET (Luas)  : {round(summary['target'], 2)} Ha")
print(f"KONTRAK        : Rp {summary['kontrak']:,.0f}")
print(f"REALISASI      : {round(summary['realized'], 2)}")
print(f"ACTIVE PAKET   : {summary['active']}")
