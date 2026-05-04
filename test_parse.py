import requests, pandas as pd, io

url = 'https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=PAKET_SULSEL5'

def parse_row_numbers(row):
    nums = []
    for val in row:
        try:
            cleaned = str(val).replace(',', '.').replace(' ', '').strip()
            if cleaned and cleaned.lower() != 'nan':
                num = float(cleaned)
                nums.append(num)
        except (ValueError, TypeError):
            pass
    return nums

req = requests.get(url)
req.encoding = 'utf-8'
df = pd.read_csv(io.StringIO(req.text))

komulatif_rencana = []
rencana_mingguan = []
rencana_bobot_idx = -1

for index, row in df.iterrows():
    row_joined = ' '.join(str(cell).upper().strip() for cell in row)
    
    if 'KOMULATIF RENCANA' in row_joined:
        komulatif_rencana = parse_row_numbers(row)
        
    if 'RENCANA BOBOT' in row_joined:
        rencana_bobot_idx = index
        
    if rencana_bobot_idx >= 0 and index == rencana_bobot_idx + 2:
        rencana_mingguan = parse_row_numbers(row)

print('KOMULATIF RENCANA:', komulatif_rencana)
print('RENCANA MINGGUAN:', rencana_mingguan)
print('RENCANA BOBOT idx:', rencana_bobot_idx)

if komulatif_rencana:
    src = komulatif_rencana
elif rencana_mingguan:
    src = rencana_mingguan
else:
    src = []

target_cumulative = []
current = 0
for val in src:
    current += val
    target_cumulative.append(round(current, 2))

print('TARGET CUMULATIVE:', target_cumulative)
print('LABELS:', [f'M{i+1}' for i in range(len(target_cumulative))])
