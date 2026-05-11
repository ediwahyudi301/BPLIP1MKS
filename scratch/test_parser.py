import requests
import pandas as pd
import io
import re

def test_parser_logic():
    # Use the correct GID and URL
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid=1894372110"
    minggu = 1
    
    req = requests.get(url)
    df = pd.read_csv(io.StringIO(req.text), header=None)
    
    # Logic from app.py
    v_idx, h_idx, b_idx, rl_idx, rm_idx, rt_idx, d_idx = 11, 12, 14, 16, 18, 20, 24
    no_col_idx = 1
    uraian_col_idx = 2
    
    header_minggu_search = f"KEMAJUAN PROGRES MINGGU {minggu}"
    in_section = False
    realisasi_data = []
    
    for index, row in df.iterrows():
        row_joined = ' '.join(str(cell).upper() for cell in row)
        
        if header_minggu_search.upper() in row_joined:
            in_section = True
            print(f"Section found at row {index}")
            continue
            
        if in_section:
            if 'JUMLAH' in row_joined and 'HARGA' in row_joined:
                # If we hit another jumlah after data, we might be at the end of a section
                if len(realisasi_data) > 0:
                    print(f"End of section at row {index}")
                    break
            
            no_val = str(row.iloc[no_col_idx]).strip()
            uraian_val = str(row.iloc[uraian_col_idx]).strip()
            
            if no_val == '1' and (uraian_val == '2' or 'URAIAN' in uraian_val.upper()):
                continue

            if no_val.isdigit() or (len(no_val) == 1 and no_val.isalpha() and no_val.isupper()):
                data = {
                    'no': no_val,
                    'uraian': uraian_val,
                    'bobot': str(row.iloc[b_idx]).strip(),
                    'realisasi_lalu': str(row.iloc[rl_idx]).strip(),
                    'realisasi_ini': str(row.iloc[rm_idx]).strip(),
                    'realisasi_total': str(row.iloc[rt_idx]).strip(),
                    'deviasi': str(row.iloc[d_idx]).strip()
                }
                realisasi_data.append(data)
                
    print(f"Total items found: {len(realisasi_data)}")
    if realisasi_data:
        print(f"First item: {realisasi_data[0]}")

if __name__ == "__main__":
    test_parser_logic()
