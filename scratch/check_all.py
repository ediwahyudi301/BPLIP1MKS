import requests
import pandas as pd
import io
import re

# GID Mapping for Sulsel 6-18
SULSEL_GID_MAPPING = {
    6: '1894372110',
    7: '451685553',
    8: '1047753912',
    9: '731318337',
    10: '628189697',
    11: '90232503',
    12: '152128190',
    13: '16428034',
    14: '510399194',
    15: '1625271799',
    16: '358284220',
    17: '1382168881',
    18: '486747432'
}

def check_all_packages():
    for nomor, gid in SULSEL_GID_MAPPING.items():
        url = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid={gid}"
        try:
            r = requests.get(url)
            df = pd.read_csv(io.StringIO(r.text), header=None)
            
            # Check for Minggu 1 header
            header_search = "KEMAJUAN PROGRES MINGGU 1"
            found = False
            for index, row in df.iterrows():
                row_joined = ' '.join(str(cell).upper() for cell in row)
                if header_search.upper() in row_joined:
                    found = True
                    break
            
            print(f"Paket {nomor}: Header '{header_search}' found? {found}")
            
            # Also check if it has KURVA S data (KOMULATIF RENCANA)
            kurva_found = False
            for index, row in df.iterrows():
                row_joined = ' '.join(str(cell).upper() for cell in row)
                if "KOMULATIF RENCANA" in row_joined:
                    kurva_found = True
                    break
            print(f"Paket {nomor}: Kurva S data found? {kurva_found}")
            
        except Exception as e:
            print(f"Paket {nomor}: Error {e}")

if __name__ == "__main__":
    check_all_packages()
