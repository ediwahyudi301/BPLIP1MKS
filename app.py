from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()  # Baca .env otomatis saat development lokal

import pandas as pd
import requests
import io
import os

# Konfigurasi Groq AI (API Key diambil dari Environment Variable)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # Model utama Groq yang kencang

# Konfigurasi Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Cache sederhana untuk AI
ai_response_cache = {} # Format: { 'normalized_message': (timestamp, 'answer') }
CACHE_TTL_MINUTES = 10

app = Flask(__name__)

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1b8XGbfCcCshv9MXfdQ8sHR5KfiT-l6zBf39YcrvicmJccREctopoq79hCEfzq5hnya_hM_LxtwML/pub?gid=684955607&single=true&output=csv"

# Cache sederhana untuk mempercepat loading
cache_dashboard = {'data': None, 'time': None}
cache_master_sulsel = {'data': None, 'time': None}
CACHE_TIMEOUT = 300 # 5 menit (dalam detik)

# Pemetaan (Mapping) Paket ke ID Folder Google Drive
# Default: 1HCmAUjk0Yd4O4OzQXQ2jEIXDIaaLq2RO (Folder Utama)
DRIVE_FOLDER_MAPPING = {
    'sulsel_1': '1HCmAUjk0Yd4O4OzQXQ2jEIXDIaaLq2RO', # Ganti dengan ID folder Paket Sulsel 1
}

MASTER_SULSEL_URL = "https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=MASTER_PAKET_SULSEL"
STATUS_PETAK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&gid=123456789" # GID placeholder

def get_peta_status():
    """Fetch status per petak from Google Sheets."""
    try:
        url = STATUS_PETAK_URL
        req = requests.get(url)
        if req.status_code != 200: return {}
        df = pd.read_csv(io.StringIO(req.text))
        if 'N_PETAK' in df.columns and 'STATUS' in df.columns:
            return df.set_index('N_PETAK')['STATUS'].to_dict()
        return {}
    except: return {}


def get_sulsel_master_summary():
    # Cek Cache
    now = datetime.now()
    if cache_master_sulsel['data'] and cache_master_sulsel['time'] and (now - cache_master_sulsel['time']).seconds < CACHE_TIMEOUT:
        return cache_master_sulsel['data']

    try:
        old_url = "https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=MASTER_PAKET_SULSEL"
        new_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&sheet=MASTER_PAKET_SULSEL"
        
        summary = {'target': 0.0, 'kontrak': 0.0, 'realized': 0.0, 'active': 0}
        
        def clean_num(s):
            """Konversi string angka ke float. Mendukung format Indonesia (1.234,56) dan standar (1234.56)."""
            s = str(s).replace('Rp', '').strip()
            if not s or s.lower() == 'nan' or s == '-':
                return None
            # Deteksi format: jika ada koma dan koma muncul setelah titik -> format Indonesia
            if ',' in s and '.' in s:
                # Format Indonesia: 9.271.106.437,00
                s = s.replace('.', '').replace(',', '.')
            elif ',' in s:
                # Hanya koma -> koma sebagai desimal: 326,86
                s = s.replace(',', '.')
            # Titik saja -> standar desimal (187.00) - biarkan apa adanya
            try:
                return float(s)
            except (ValueError, TypeError):
                return None

        def process_df(df, min_no, max_no, col_luas, col_kontrak, col_realisasi, skip_rows=3):
            """Parse rows dari df berdasarkan range nomor paket dan mapping kolom."""
            for index, row in df.iterrows():
                if index < skip_rows: continue
                no_str = str(row.iloc[1]).strip()
                if no_str.lower() != 'nan':
                    try:
                        pkg_no = int(float(no_str))
                        if min_no <= pkg_no <= max_no:
                            # Target (Luas)
                            v = clean_num(row.iloc[col_luas] if len(row) > col_luas else None)
                            if v is not None: summary['target'] += v
                            
                            # Kontrak
                            v = clean_num(row.iloc[col_kontrak] if len(row) > col_kontrak else None)
                            if v is not None: summary['kontrak'] += v
                            
                            # Realized
                            v = clean_num(row.iloc[col_realisasi] if len(row) > col_realisasi else None)
                            if v is not None: summary['realized'] += v
                        
                        summary['active'] += 1
                    except:
                        pass
        
        # Old URL: paket 1-5 (col 10=Luas, col 9=Kontrak, col 12=Realisasi)
        req1 = requests.get(old_url)
        df1 = pd.read_csv(io.StringIO(req1.text), header=None)
        process_df(df1, 1, 5, col_luas=10, col_kontrak=9, col_realisasi=12)
        
        # New URL: paket 6-24 (col 7=Luas, col 6=Kontrak, col 9=Realisasi)
        req2 = requests.get(new_url)
        df2 = pd.read_csv(io.StringIO(req2.text), header=None)
        process_df(df2, 6, 24, col_luas=7, col_kontrak=6, col_realisasi=9, skip_rows=8)
        
        # Simpan ke Cache
        cache_master_sulsel['data'] = summary
        cache_master_sulsel['time'] = now
        
        return summary
    except Exception as e:
        print("Error fetching Sulsel Master Summary:", e)
        return None

def fetch_dashboard_data():
    # Cek Cache
    now = datetime.now()
    if cache_dashboard['data'] and cache_dashboard['time'] and (now - cache_dashboard['time']).seconds < CACHE_TIMEOUT:
        return cache_dashboard['data']

    try:
        req = requests.get(SHEET_CSV_URL)
        req.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(req.text))
        
        master_sulsel = get_sulsel_master_summary()
        
        # Berdasarkan permintaan user: Target Dashboard untuk sementara = Target MASTER_PAKET_SULSEL
        if master_sulsel:
            total_target = master_sulsel['target']
            total_kontrak = master_sulsel['kontrak']
            total_realized = master_sulsel['realized']
        else:
            total_target = 0
            total_kontrak = 0
            total_realized = 0
            
        regional_status = []
        active_projects = 0
        
        current_region = None
        region_data = {}
        
        for index, row in df.iterrows():
            no_val = str(row['No']).strip()
            
            # Abaikan baris kosong
            if not no_val or no_val.lower() == 'nan':
                continue
                
            # Deteksi Header Wilayah (Non-angka)
            if not no_val.isdigit():
                if region_data:
                    regional_status.append(region_data)
                
                # Parsing Angka Luas_Ha format indonesia "7.859,51" menjadi float
                target_str = str(row['Luas_Ha']).replace('.', '').replace(',', '.').replace(' ', '').strip()
                try:
                    target_val = float(target_str)
                except ValueError:
                    target_val = 0.0
                
                current_region = no_val.title()
                
                # Integrasi Data Master Sulsel (Timpa data jika ada)
                if "Sulawesi Selatan" in current_region and master_sulsel:
                    target_val = master_sulsel['target']
                
                # total_target += target_val # Dihapus sementara, target dashboard hanya dari MASTER SULSEL
                
                region_data = {
                    'region': current_region,
                    'target': target_val,
                    'kontrak': 0,
                    'realized': 0, 
                    'status': 'Persiapan'
                }
                
                if "Sulawesi Selatan" in current_region and master_sulsel:
                    region_data['kontrak'] = master_sulsel['kontrak']
                    region_data['realized'] = master_sulsel['realized']
                    region_data['status'] = 'Konstruksi' if master_sulsel['realized'] > 0 else 'Penayangan'
            else:
                # Menghitung Baris Paket Proyek Aktif (Hanya untuk wilayah aktif: Sulsel & Sulteng)
                if current_region and ("Sulawesi Selatan" in current_region or "Sulawesi Tengah" in current_region):
                    active_projects += 1
                
                # Logika Status Penayangan berdasarkan Kesimpulan (untuk wilayah non-master)
                if not ("Sulawesi Selatan" in str(current_region)):
                    kesimpulan = str(row['Kesimpulan']).strip().lower()
                    if ('tayang' in kesimpulan) or ('lelang' in kesimpulan) or ('evaluasi' in kesimpulan):
                        if region_data and region_data['status'] == 'Persiapan':
                            region_data['status'] = 'Penayangan'
                            
                    # Parse Nilai Kontrak wilayah non-master
                    kontrak_str = str(row['Kontrak']).replace('.', '').replace(',', '.').replace('Rp', '').replace(' ', '').strip()
                    try:
                        if kontrak_str.lower() == 'nan':
                            kontrak_val = 0.0
                        else:
                            kontrak_val = float(kontrak_str)
                    except ValueError:
                        kontrak_val = 0.0
                    
                    if region_data:
                        region_data['kontrak'] += kontrak_val

                # Menghitung realisasi (jika ada data kedepannya)
                # Contoh: saat ini data 'realized' di sheet memang belum ada representasi eksplisit
                
        # Menambahkan data wilayah terakhir ke array
        if region_data:
            regional_status.append(region_data)
            
        # Tampilkan kembali semua wilayah (Sulsel, Sulbar, Sulteng, Sultra)
        allowed_regions = ["Sulawesi Selatan", "Sulawesi Tengah", "Sulawesi Barat", "Sulawesi Tenggara"]
        regional_status = [r for r in regional_status if any(ar in r['region'] for ar in allowed_regions)]
        
        # Hitung ulang active_projects hanya untuk wilayah yang diperbolehkan
        # Namun karena active_projects dihitung di dalam loop di atas, 
        # kita perlu logika filter di dalam loop tersebut.
            
        # Calculate overall dashboard totals properly
        # total_realized = sum(r['realized'] for r in regional_status) # Dihapus sementara
        # total_kontrak = sum(r['kontrak'] for r in regional_status) # Dihapus sementara
        
        overall_progress = 0
        if total_target > 0:
            overall_progress = round((total_realized / total_target) * 100, 1)
            
        # Simpan ke Cache
        result = {
            'summary': {
                'total_area_target': total_target, 
                'total_area_realized': total_realized,
                'total_kontrak': total_kontrak,
                'active_projects': active_projects,
                'overall_progress': overall_progress 
            },
            'monthly_progress': {
                # Setup sementara (karena google sheets belum memuat timeline bulanan)
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                'target': [1000, 3000, 5000, 7000, 9000, 12599, 12599, 12599],
                'realized': [0, 0, 0, 0, 0, 0, 0, 0] 
            },
            'regional_status': regional_status
        }
        cache_dashboard['data'] = result
        cache_dashboard['time'] = now
        
        return result
    except Exception as e:
        print("Error fetching data dari API:", e)
        # Fallback jika terjadi kesalahan koneksi
        return {
            'summary': { 'total_area_target': 12599.05, 'total_area_realized': 0, 'active_projects': 35, 'overall_progress': 0 },
            'monthly_progress': { 'labels': ['Jan'], 'target': [0], 'realized': [0] },
            'regional_status': [ {'region': 'Koneksi Gagal', 'target': 0, 'realized': 0, 'status': 'Error'} ]
        }

def get_realisasi_data(paket_id, minggu=1):
    # Mapping paket_id to sheet names (similar to kurva_s logic)
    sheet_name = ""
    if paket_id.startswith('sulsel_'):
        nomor = paket_id.split('_')[1]
        sheet_name = f"PAKET_SULSEL{nomor}"
    elif paket_id.startswith('sulbar_'):
        nomor = paket_id.split('_')[1]
        sheet_name = f"PAKET_SULBAR{nomor}"
    elif paket_id.startswith('sulteng_'):
        nomor = paket_id.split('_')[1]
        sheet_name = f"PAKET_SULTENG{nomor}"
    elif paket_id.startswith('sultra_'):
        nomor = paket_id.split('_')[1]
        sheet_name = f"PAKET_SULTRA{nomor}"
    
    if not sheet_name:
        return {"error": "Paket ID tidak valid"}

    # Base URL for Google Sheets CSV
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
    
    if paket_id.startswith('sulsel_'):
        nomor = int(paket_id.split('_')[1])
        if nomor >= 6:
            gid = SULSEL_GID_MAPPING.get(nomor, '')
            url = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid={gid}"
        else:
            url = f"https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    else:
        url = f"https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    try:
        req = requests.get(url)
        req.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(req.text))
        
        realisasi_data = []
        project_info = {}
        available_weeks = []
        in_section = False
        section_found = False
        
        # Determine format/offsets
        v_idx, h_idx, b_idx, rl_idx, rm_idx, rt_idx, d_idx = 11, 12, 16, 18, 19, 21, 23 # Default SULSEL1?
        if 'SULSEL5' in sheet_name:
            v_idx, h_idx, b_idx, rl_idx, rm_idx, rt_idx, d_idx = 11, 13, 14, 17, 19, 18, 24
        elif paket_id.startswith('sulsel_') and int(paket_id.split('_')[1]) >= 6:
            # Layout untuk Paket 6-18 di Spreadsheet Baru
            # No: 1, Uraian: 2, Vol: 11, Harga: 12, Bobot: 14, RL: 16, RM: 18, RT: 20, Dev: 24
            v_idx, h_idx, b_idx, rl_idx, rm_idx, rt_idx, d_idx = 11, 12, 14, 16, 18, 20, 24
            no_col_idx = 1 # Column B
            uraian_col_idx = 2 # Column C
        else:
            # Default indexing
            no_col_idx = 1
            uraian_col_idx = 2
            
        import re
        # First pass: find all available weeks
        for index, row in df.iterrows():
            row_joined = ' '.join(str(cell).upper() for cell in row)
            if 'KEMAJUAN PROGRES MINGGU' in row_joined:
                # Extract number from "MINGGU 1" or "MINGGU 1 (SATU)"
                match = re.search(r'MINGGU\s+(\d+)', row_joined)
                if match:
                    available_weeks.append(int(match.group(1)))

        header_minggu_search = f"KEMAJUAN PROGRES MINGGU {minggu}"
        
        for index, row in df.iterrows():
            row_joined = ' '.join(str(cell).upper() for cell in row)
            
            # Find the section start
            if header_minggu_search.upper() in row_joined:
                in_section = True
                section_found = True
                continue
                
            if in_section:
                # Helper to get value after label
                def get_val(r, label):
                    for i, cell in enumerate(r):
                        if label.upper() in str(cell).upper():
                            for j in range(i + 1, len(r)):
                                val = str(r.iloc[j]).strip()
                                if val and val != ':' and val.lower() != 'nan':
                                    return val
                    return ""

                # Parse project info
                if 'SATUAN KERJA' in row_joined and not project_info.get('satuan_kerja'):
                    project_info['satuan_kerja'] = get_val(row, 'SATUAN KERJA')
                elif 'PEKERJAAN' in row_joined and 'URAIAN' not in row_joined and not project_info.get('pekerjaan'):
                    project_info['pekerjaan'] = get_val(row, 'PEKERJAAN')
                elif 'LOKASI' in row_joined and not project_info.get('lokasi'):
                    project_info['lokasi'] = get_val(row, 'LOKASI')
                elif 'NOMOR KONTRAK' in row_joined and not project_info.get('nomor_kontrak'):
                    project_info['nomor_kontrak'] = get_val(row, 'NOMOR KONTRAK')
                elif 'PELAKSANA' in row_joined and not project_info.get('pelaksana'):
                    project_info['pelaksana'] = get_val(row, 'PELAKSANA')
                elif 'PENGAWAS' in row_joined and not project_info.get('pengawas'):
                    project_info['pengawas'] = get_val(row, 'PENGAWAS')
                
                # Detect the table start (No 1, 2, 3...)
                no_val = str(row.iloc[no_col_idx]).strip()
                uraian_val = str(row.iloc[uraian_col_idx]).strip()
                
                # Skip header labels
                if no_val == '1' and (uraian_val == '2' or 'URAIAN' in uraian_val.upper()):
                    continue

                if no_val.isdigit() or (len(no_val) == 1 and no_val.isalpha() and no_val.isupper()):
                    # Helper to clean numeric strings
                    def clean_numeric_str(v):
                        v_s = str(v).strip()
                        if not v_s or v_s.lower() == 'nan' or v_s == '-':
                            return "0"
                        return v_s

                    # Extract data row using determined indices
                    rl_val = clean_numeric_str(row.iloc[rl_idx] if len(row) > rl_idx else "0")
                    rm_val = clean_numeric_str(row.iloc[rm_idx] if len(row) > rm_idx else "0")
                    rt_val = clean_numeric_str(row.iloc[rt_idx] if len(row) > rt_idx else "0")
                    

                    # Calculate total if zero or placeholder
                    if rt_val == "0":
                        try:
                            # Clean for float conversion (comma to dot)
                            rl_f = float(rl_val.replace(',', '.'))
                            rm_f = float(rm_val.replace(',', '.'))
                            if rl_f > 0 or rm_f > 0:
                                rt_val = str(round(rl_f + rm_f, 3)).replace('.', ',')
                        except:
                            pass

                    item = {
                        'no': no_val,
                        'uraian': uraian_val,
                        'volume': str(row.iloc[v_idx]).strip() if len(row) > v_idx else "",
                        'harga': str(row.iloc[h_idx]).strip() if len(row) > h_idx else "",
                        'bobot': str(row.iloc[b_idx]).strip() if len(row) > b_idx else "",
                        'realisasi_sd_lalu': rl_val,
                        'realisasi_minggu': rm_val,
                        'realisasi_total': rt_val,
                        'deviasi': str(row.iloc[d_idx]).strip() if len(row) > d_idx else ""
                    }
                    # Filter out empty or header-like rows
                    if item['uraian'] and 'URAIAN' not in item['uraian'].upper() and item['uraian'] != 'nan':
                        realisasi_data.append(item)
                
                # Check for section end
                if 'TOTAL HARGA' in row_joined or ('KEMAJUAN PROGRES MINGGU' in row_joined and header_minggu_search.upper() not in row_joined):
                    if len(realisasi_data) > 0:
                        break

        if not section_found:
            return {"error": f"Data untuk Minggu {minggu} tidak ditemukan", "available_weeks": available_weeks}

        return {
            "project_info": project_info,
            "realisasi_data": realisasi_data,
            "minggu": minggu,
            "available_weeks": sorted(list(set(available_weeks)))
        }
        
    except Exception as e:
        return {"error": str(e)}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/peta')
def peta():
    return render_template('peta.html')

@app.route('/kurva_s')
def kurva_s():
    paket = request.args.get('paket', 'sulsel_1')
    return render_template('kurva_s.html', paket=paket)

@app.route('/master_sulsel')
def master_sulsel():
    return render_template('master_sulsel.html')

@app.route('/master_sulteng')
def master_sulteng():
    return render_template('master_sulteng.html')

@app.route('/api/master_sulsel')
def get_master_sulsel():
    old_url = "https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet=MASTER_PAKET_SULSEL"
    new_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&sheet=MASTER_PAKET_SULSEL"
    try:
        data = []
        
        # Process Old Link (Get 1-5)
        try:
            req1 = requests.get(old_url)
            df1 = pd.read_csv(io.StringIO(req1.text), header=None)
            for index, row in df1.iterrows():
                if index < 3: continue
                no_str = str(row.iloc[1]).strip()
                if no_str.lower() != 'nan':
                    try:
                        pkg_no = int(float(no_str))
                        if pkg_no <= 5:
                            data.append({
                                'no': str(pkg_no),
                                'paket': str(row.iloc[2]).strip() if len(row) > 2 else '-',
                                'penyedia': str(row.iloc[8]).strip() if len(row) > 8 and str(row.iloc[8]).strip().lower() != 'nan' else '-',
                                'harga': str(row.iloc[9]).strip() if len(row) > 9 and str(row.iloc[9]).strip().lower() != 'nan' else '-',
                                'rencana': str(row.iloc[11]).strip() if len(row) > 11 and str(row.iloc[11]).strip().lower() != 'nan' else '0',
                                'realisasi': str(row.iloc[12]).strip() if len(row) > 12 and str(row.iloc[12]).strip().lower() != 'nan' else '0',
                                'deviasi': str(row.iloc[13]).strip() if len(row) > 13 and str(row.iloc[13]).strip().lower() != 'nan' else '0'
                            })
                    except ValueError:
                        pass
        except Exception as e:
            pass

        # Process New Link (Get 6-24)
        # New URL column layout: col1=NO, col2=NamaPaket, col5=Pelaksana, col6=NilaiKontrak, col7=Luas, col8=Rencana, col9=Realisasi, col10=Deviasi
        try:
            req2 = requests.get(new_url)
            df2 = pd.read_csv(io.StringIO(req2.text), header=None)
            for index, row in df2.iterrows():
                if index < 8: continue  # Skip header rows (new URL has more header rows)
                no_str = str(row.iloc[1]).strip()
                if no_str.lower() != 'nan':
                    try:
                        pkg_no = int(float(no_str))
                        if pkg_no >= 6:
                            data.append({
                                'no': str(pkg_no),
                                'paket': str(row.iloc[2]).strip() if len(row) > 2 else '-',
                                'penyedia': str(row.iloc[5]).strip() if len(row) > 5 and str(row.iloc[5]).strip().lower() != 'nan' else '-',
                                'harga': str(row.iloc[6]).strip() if len(row) > 6 and str(row.iloc[6]).strip().lower() != 'nan' else '-',
                                'rencana': str(row.iloc[8]).strip() if len(row) > 8 and str(row.iloc[8]).strip().lower() != 'nan' else '0',
                                'realisasi': str(row.iloc[9]).strip() if len(row) > 9 and str(row.iloc[9]).strip().lower() != 'nan' else '0',
                                'deviasi': str(row.iloc[10]).strip() if len(row) > 10 and str(row.iloc[10]).strip().lower() != 'nan' else '0'
                            })
                    except ValueError:
                        pass
        except Exception as e:
            pass

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/master_sulteng')
def get_master_sulteng():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVjsO3yxV0AAmuj3iJjpl2n5P8x-uG2EyQR93uM0Vx41F0J0SptF9rD9t0p3QUx3Zmpc0VAuvjH2vl/pub?output=csv&single=true&sheet=MASTER_PAKET_SULTENG"
    try:
        req = requests.get(url)
        df = pd.read_csv(io.StringIO(req.text), header=None)
        
        data = []
        for index, row in df.iterrows():
            if index < 3: continue # Skip headers
            no_val = str(row.iloc[1]).strip() if len(row) > 1 else 'nan'
            if no_val and no_val.lower() != 'nan' and (no_val.isdigit() or ('.' in no_val and no_val.replace('.', '').isdigit())):
                data.append({
                    'no': no_val,
                    'paket': str(row.iloc[2]).strip() if len(row) > 2 else '-',
                    'penyedia': str(row.iloc[5]).strip() if len(row) > 5 and str(row.iloc[5]).strip().lower() != 'nan' else '-',
                    'harga': str(row.iloc[6]).strip() if len(row) > 6 and str(row.iloc[6]).strip().lower() != 'nan' else '-',
                    'rencana': str(row.iloc[8]).strip() if len(row) > 8 and str(row.iloc[8]).strip().lower() != 'nan' else '0',
                    'realisasi': str(row.iloc[9]).strip() if len(row) > 9 and str(row.iloc[9]).strip().lower() != 'nan' else '0',
                    'deviasi': str(row.iloc[10]).strip() if len(row) > 10 and str(row.iloc[10]).strip().lower() != 'nan' else '0'
                })
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/data')
def get_data():
    return jsonify(fetch_dashboard_data())

@app.route('/api/peta_status')
def api_peta_status():
    return jsonify(get_peta_status())

@app.route('/api/kurva_s/<paket_id>')
def get_kurva_s(paket_id):
    # Mapping paket_id to sheet name, default to PAKET_SULSEL1
    sheet_name = 'PAKET_SULSEL1'
    if paket_id.startswith('sulsel_'):
        nomor = paket_id.split('_')[1]
        sheet_name = f'PAKET_SULSEL{nomor}'
    elif paket_id.startswith('sulbar_'):
        nomor = paket_id.split('_')[1]
        sheet_name = f'PAKET_SULBAR{nomor}'
    elif paket_id.startswith('sulteng_'):
        nomor = paket_id.split('_')[1]
        sheet_name = f'PAKET_SULTENG{nomor}'
    elif paket_id.startswith('sultra_'):
        nomor = paket_id.split('_')[1]
        sheet_name = f'PAKET_SULTRA{nomor}'
    
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
    
    if paket_id.startswith('sulsel_'):
        nomor = int(paket_id.split('_')[1])
        if nomor >= 6:
            gid = SULSEL_GID_MAPPING.get(nomor, '')
            url = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vS0JKAKWKm4WZMXtFp_jFYgz7_RNpse8FBl9jw6M8TkTwZWTQEhoEUGQuNNMJLLQRVg0kE4bs-HdDsz/pub?output=csv&single=true&gid={gid}"
        else:
            url = f"https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    else:
        url = f"https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    def parse_row_numbers(row):
        """Extract numeric values from a row, skipping non-numeric cells."""
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

    try:
        req = requests.get(url)
        req.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(req.text))
        
        # Data containers
        komulatif_rencana = []  # Cumulative target values from sheet
        realisasi_values = []   # Realisasi values from sheet
        deviasi_values = []     # Deviasi values from sheet
        komulatif_values = []   # Komulatif realisasi from sheet
        rencana_mingguan = []   # Weekly plan values
        rencana_bobot_idx = -1  # Index of RENCANA BOBOT row
        
        # Contract date containers
        tanggal_mulai = None
        tanggal_berakhir = None
        pengawas_konstruksi = None
        
        # Equipment data containers
        equipment_list = []
        in_equipment_section = False
        equipment_header_found = False
        
        for index, row in df.iterrows():
            row_str = row.astype(str).str.upper()
            row_joined = ' '.join(str(cell).upper().strip() for cell in row)
            
            # Parse Tanggal Mulai
            if 'TANGGAL MULAI' in row_joined:
                for cell in row:
                    cell_str = str(cell).strip()
                    if cell_str and cell_str.lower() != 'nan' and 'tanggal' not in cell_str.lower() and cell_str != ':':
                        # Try parsing date formats: M/D/YYYY, DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
                        for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                            try:
                                tanggal_mulai = datetime.strptime(cell_str, fmt)
                                break
                            except ValueError:
                                continue
                    if tanggal_mulai:
                        break
            
            # Parse Tanggal Berakhir
            if 'TANGGAL BERAKHIR' in row_joined:
                for cell in row:
                    cell_str = str(cell).strip()
                    if cell_str and cell_str.lower() != 'nan' and 'tanggal' not in cell_str.lower() and cell_str != ':':
                        for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                            try:
                                tanggal_berakhir = datetime.strptime(cell_str, fmt)
                                break
                            except ValueError:
                                continue
                    if tanggal_berakhir:
                        break
                        
            # Parse Pengawas Konstruksi
            if 'PENGAWAS KONSTRUKSI' in row_joined:
                # Find the first cell that is not 'nan', not empty, not ':', and doesn't contain 'pengawas'
                for cell in row:
                    cell_str = str(cell).strip()
                    if cell_str and cell_str.lower() != 'nan' and cell_str != ':' and 'pengawas' not in cell_str.lower():
                        pengawas_konstruksi = cell_str
                        break
            
            # Format A (SULSEL1 style): explicit labeled rows
            if 'KOMULATIF RENCANA' in row_joined:
                komulatif_rencana = parse_row_numbers(row)
                
            if 'REALISASI MINGGUAN' not in row_joined and 'REALISASI' in row_joined:
                # Make sure it's the cumulative REALISASI row, not REALISASI MINGGUAN
                if not any('MINGGUAN' in str(cell).upper() for cell in row):
                    realisasi_values = parse_row_numbers(row)
                
            if 'DEVIASI' in row_joined:
                deviasi_values = parse_row_numbers(row)
                
            # Read KOMULATIF row (cumulative realisasi)
            if row_joined.strip().startswith('KOMULATIF') and 'RENCANA' not in row_joined:
                komulatif_values = parse_row_numbers(row)
            
            # Format B (SULSEL5 style): detect RENCANA BOBOT row
            if 'RENCANA BOBOT' in row_joined:
                rencana_bobot_idx = index
                
            # Row after RENCANA BOBOT contains weekly plan data (Format B)
            if rencana_bobot_idx >= 0 and index == rencana_bobot_idx + 2:
                rencana_mingguan = parse_row_numbers(row)
            
            # Parse Kebutuhan Alat section
            if 'KEBUTUHAN ALAT' in row_joined:
                in_equipment_section = True
                continue
            
            # Detect equipment header row (No, Jenis, Spesifikasi)
            if in_equipment_section and not equipment_header_found:
                if 'JENIS' in row_joined or 'SPESIFIKASI' in row_joined:
                    equipment_header_found = True
                    continue
            
            # Parse equipment data rows
            if in_equipment_section and equipment_header_found:
                cells = [str(cell).strip() for cell in row]
                # Filter out empty/nan cells
                non_empty = [c for c in cells if c and c.lower() != 'nan']
                
                if len(non_empty) < 3:
                    # End of equipment section (empty row or insufficient data)
                    in_equipment_section = False
                    continue
                
                # Parse the equipment row: No, Jenis, Spesifikasi, Kebutuhan, Tersedia
                no_val = ''
                jenis = ''
                spesifikasi = ''
                kebutuhan = 0
                tersedia = 0
                
                # Find values by position in the row
                data_cells = []
                for cell in cells:
                    if cell and cell.lower() != 'nan':
                        data_cells.append(cell)
                
                if len(data_cells) >= 3:
                    no_val = data_cells[0]
                    jenis = data_cells[1]
                    spesifikasi = data_cells[2]
                    
                    # Parse numeric values for kebutuhan and tersedia
                    nums = []
                    for dc in data_cells[3:]:
                        try:
                            num = float(dc.replace(',', '.').replace(' ', ''))
                            nums.append(num)
                        except (ValueError, TypeError):
                            pass
                    
                    if len(nums) >= 1:
                        kebutuhan = nums[0]
                    if len(nums) >= 2:
                        tersedia = nums[1]
                    
                    equipment_list.append({
                        'no': no_val,
                        'jenis': jenis,
                        'spesifikasi': spesifikasi,
                        'kebutuhan': kebutuhan,
                        'tersedia': tersedia
                    })
        
        # Determine target cumulative
        if komulatif_rencana:
            # Format A: KOMULATIF RENCANA row contains weekly values, accumulate them
            target_cumulative = []
            current = 0
            for val in komulatif_rencana:
                current += val
                target_cumulative.append(round(current, 2))
        elif rencana_mingguan:
            # Format B: Use weekly values from row after RENCANA BOBOT
            target_cumulative = []
            current = 0
            for val in rencana_mingguan:
                current += val
                target_cumulative.append(round(current, 2))
        else:
            target_cumulative = []
        
        # Determine realized cumulative
        if realisasi_values:
            realized_cumulative = []
            current = 0
            for val in realisasi_values:
                current += val
                realized_cumulative.append(round(current, 2))
        else:
            realized_cumulative = [0] * len(target_cumulative)
        
        # Determine deviation
        if deviasi_values:
            deviation = deviasi_values
        else:
            deviation = []
            for i in range(len(realized_cumulative)):
                if i < len(target_cumulative):
                    dev = round(realized_cumulative[i] - target_cumulative[i], 2)
                    deviation.append(dev)
        
        # Estimate Tanggal Berakhir if missing (based on number of weekly columns)
        num_weeks = len(target_cumulative)
        if tanggal_mulai and not tanggal_berakhir and num_weeks > 0:
            tanggal_berakhir = tanggal_mulai + timedelta(weeks=num_weeks)
        
        # Build contract info
        contract_info = {}
        if pengawas_konstruksi:
            contract_info['pengawas'] = pengawas_konstruksi
        if tanggal_mulai:
            contract_info['tanggal_mulai'] = tanggal_mulai.strftime('%Y-%m-%d')
        if tanggal_berakhir:
            contract_info['tanggal_berakhir'] = tanggal_berakhir.strftime('%Y-%m-%d')
        if tanggal_mulai and tanggal_berakhir:
            today = datetime.now()
            total_days = (tanggal_berakhir - tanggal_mulai).days
            remaining_days = (tanggal_berakhir - today).days
            elapsed_days = (today - tanggal_mulai).days
            contract_info['total_hari_kontrak'] = total_days
            contract_info['sisa_hari_kontrak'] = max(remaining_days, 0)
            contract_info['hari_berjalan'] = max(elapsed_days, 0)
            contract_info['persentase_waktu'] = round(min(max(elapsed_days / total_days * 100, 0), 100), 1) if total_days > 0 else 0
            
        labels = [f"M{i+1}" for i in range(len(target_cumulative))]
        
        return jsonify({
            'labels': labels,
            'target': target_cumulative,
            'realized': realized_cumulative,
            'deviation': deviation,
            'contract_info': contract_info,
            'equipment': equipment_list
        })
    except Exception as e:
        print("Error fetching S-Curve data:", e)
        return jsonify({
            'labels': [],
            'target': [],
            'realized': [],
            'error': str(e)
        }), 500

# Mapping paket_id ke URL CSV spreadsheet per-petak
PETAK_SHEET_MAPPING = {
    'sulsel_1': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vS6fOtv-P_JhyRjTIMEpFsfwP2AvR0nsUho4Nf4cvfYnfu8-DjZlYRhFj8ZbTymumqUiwIWdve3qIsR/pub?gid=0&single=true&output=csv',
    'sulsel_2': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vS6fOtv-P_JhyRjTIMEpFsfwP2AvR0nsUho4Nf4cvfYnfu8-DjZlYRhFj8ZbTymumqUiwIWdve3qIsR/pub?gid=1908203472&single=true&output=csv',
    'sulsel_3': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vS6fOtv-P_JhyRjTIMEpFsfwP2AvR0nsUho4Nf4cvfYnfu8-DjZlYRhFj8ZbTymumqUiwIWdve3qIsR/pub?gid=1143415810&single=true&output=csv',
    'sulsel_4': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vS6fOtv-P_JhyRjTIMEpFsfwP2AvR0nsUho4Nf4cvfYnfu8-DjZlYRhFj8ZbTymumqUiwIWdve3qIsR/pub?gid=8251783&single=true&output=csv',
    'sulsel_5': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vS6fOtv-P_JhyRjTIMEpFsfwP2AvR0nsUho4Nf4cvfYnfu8-DjZlYRhFj8ZbTymumqUiwIWdve3qIsR/pub?gid=1413155599&single=true&output=csv',
    # Mapping untuk Sulawesi Tengah (Ganti URL dengan link CSV spreadsheet yang sesuai)
    'sulteng_1': '',
    'sulteng_2': '',
    'sulteng_3': '',
    'sulteng_4': '',
    'sulteng_5': '',
    'sulteng_6': '',
    'sulteng_7': '',
    'sulteng_8': '',
    'sulteng_9': '',
    'sulteng_10': '',
    'sulteng_11': '',
}

@app.route('/api/petak_data/all')
def api_petak_data_all():
    """Menggabungkan data dari semua spreadsheet petak untuk tampilan overview."""
    try:
        all_data = {}
        for paket_id, url in PETAK_SHEET_MAPPING.items():
            if not url: continue
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    df = pd.read_csv(io.StringIO(resp.text))
                    df.columns = [c.strip() for c in df.columns]
                    key_col = 'NO_PETAK' if 'NO_PETAK' in df.columns else ('N_PETAK' if 'N_PETAK' in df.columns else None)
                    if key_col:
                        # Ambil kolom status
                        status_cols = ['LAND_CLEARING', 'LAND_LEVELLING', 'OLAH_LAHAN']
                        available_status = [c for c in status_cols if c in df.columns]
                        for _, row in df.iterrows():
                            petak_id = str(row[key_col]).strip()
                            if petak_id:
                                d = {}
                                for c in available_status: d[c] = str(row[c]).strip()
                                all_data[petak_id] = d
            except:
                continue
        return jsonify(all_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Kolom yang ada di GeoJSON (tidak perlu ditampilkan ulang)
GEOJSON_COLS = {'KABUPATEN', 'KECAMATAN', 'DESA_KEL', 'POKTAN', 'KET_POKTAN',
                'NO_HP', 'NAMA_PEMIL', 'LUAS_Ha', 'PAKET', 'NO_PETAK', 'PROVINSI'}

@app.route('/api/petak_data/<paket_id>')
def api_petak_data(paket_id):
    """Fetch spreadsheet data per petak dan return kolom eksklusif (tidak ada di GeoJSON)."""
    try:
        url = PETAK_SHEET_MAPPING.get(paket_id)
        if not url:
            return jsonify({'error': f'Tidak ada mapping spreadsheet untuk paket {paket_id}'}), 404

        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return jsonify({'error': f'Gagal fetch spreadsheet: HTTP {resp.status_code}'}), 502

        df = pd.read_csv(io.StringIO(resp.text))

        # Bersihkan nama kolom
        df.columns = [c.strip() for c in df.columns]

        if 'NO_PETAK' not in df.columns:
            return jsonify({'error': 'Kolom NO_PETAK tidak ditemukan di spreadsheet'}), 400

        # Kirim semua kolom dari spreadsheet agar bisa membatalkan data GeoJSON yang "kotor"
        result = {}
        for _, row in df.iterrows():
            petak = str(row['NO_PETAK']).strip()
            if not petak or petak.lower() == 'nan':
                continue
            # Ambil semua kolom yang ada di baris ini
            result[petak] = {col: (str(row[col]).strip() if pd.notna(row[col]) else '-')
                             for col in df.columns}

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/laporan')
def laporan():
    paket = request.args.get('paket', 'sulsel_1')
    
    # Ambil ID folder dari dictionary, jika tidak ada fallback ke folder utama
    folder_id = DRIVE_FOLDER_MAPPING.get(paket, '1HCmAUjk0Yd4O4OzQXQ2jEIXDIaaLq2RO')
    
    # Kosongkan folder_id untuk Sulsel jika tidak ada di mapping
    if paket.startswith('sulsel_') and not DRIVE_FOLDER_MAPPING.get(paket):
        folder_id = ""
    
    return render_template('laporan.html', paket=paket, folder_id=folder_id)

@app.route('/realisasi')
def realisasi():
    paket_id = request.args.get('paket', 'sulsel_5')
    minggu = request.args.get('minggu', 1, type=int)
    
    data = get_realisasi_data(paket_id, minggu)
    
    # Calculate Display Name (similar to kurva_s route)
    paket_name = "Paket Proyek"
    if paket_id.startswith('sulsel_'):
        nomor = paket_id.split('_')[1]
        paket_name = f"Paket Sulawesi Selatan {nomor}"
    elif paket_id.startswith('sulbar_'):
        nomor = paket_id.split('_')[1]
        paket_name = f"Paket Sulawesi Barat {nomor}"
    elif paket_id.startswith('sulteng_'):
        nomor = paket_id.split('_')[1]
        paket_name = f"Paket Sulawesi Tengah {nomor}"
    elif paket_id.startswith('sultra_'):
        nomor = paket_id.split('_')[1]
        paket_name = f"Paket Sulawesi Tenggara {nomor}"
        
    return render_template('realisasi.html', 
                           data=data, 
                           paket=paket_id, 
                           paket_name=paket_name, 
                           minggu=minggu,
                           available_weeks=data.get('available_weeks', [1]))


@app.route('/api/openclaw/summary')
def api_openclaw_summary():
    """Endpoint API khusus untuk OpenClaw atau agen AI lainnya."""
    try:
        data = fetch_dashboard_data()
        summary_data = data.get('summary', {})
        
        summary = {
            'waktu_pengambilan': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_target_ha': summary_data.get('total_area_target', 0),
            'total_realisasi_ha': summary_data.get('total_area_realized', 0),
            'provinsi_aktif': summary_data.get('active_projects', 0),
            'rincian_provinsi': data.get('regional_status', []),
            'pesan_sistem': 'Ini adalah ringkasan resmi dari WebGIS Monev BPLIP1 Makassar.'
        }
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agent/test')
def api_agent_test():
    """Endpoint untuk mengetes koneksi ke Groq API."""
    if not GROQ_API_KEY:
        return jsonify({'status': 'error', 'message': 'GROQ_API_KEY tidak ditemukan di environment variables'})
    try:
        resp = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            timeout=10
        )
        return jsonify({'status': resp.status_code, 'body': resp.json()})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/agent/chat', methods=['POST'])
def api_agent_chat():
    """Endpoint untuk Asisten AI Nina - menggunakan Groq REST API."""
    try:
        req_data = request.get_json()
        user_message = req_data.get('message', '')

        if not GROQ_API_KEY:
            return jsonify({'response': '⚠️ API Key Groq belum dikonfigurasi. Silakan tambahkan GROQ_API_KEY di environment variables Vercel, lalu Redeploy.'})

        # Ambil data real-time
        dashboard_data = fetch_dashboard_data()
        
        # Susun konteks data
        context_lines = []
        for prov in dashboard_data.get('regional_status', []):
            context_lines.append(f"- {prov.get('region')}: Target {prov.get('target')} Ha, Realisasi {prov.get('realized')} Ha (Status: {prov.get('status')})")
        
        system_prompt = f"""Kamu adalah Nina, Asisten AI ramah dan profesional untuk WebGIS Monev BPLIP1 Makassar.
Tugasmu adalah menjawab pertanyaan pengguna seputar proyek cetak sawah.

Data REAL-TIME saat ini:
- Total Target: {dashboard_data.get('summary', {}).get('total_area_target', 0)} Ha
- Total Realisasi: {dashboard_data.get('summary', {}).get('total_area_realized', 0)} Ha
- Proyek Aktif: {dashboard_data.get('summary', {}).get('active_projects', 0)}

Rincian per provinsi:
{chr(10).join(context_lines)}

Gunakan data di atas untuk menjawab. Jawablah dengan singkat, ramah, dan langsung ke intinya. Gunakan format Markdown (bold, list) jika perlu. Jangan mengarang data yang tidak ada."""
        
        # Cek Cache sebelum panggil Groq API
        msg_key = user_message.lower().strip()
        now = datetime.now()
        if msg_key in ai_response_cache:
            timestamp, cached_reply = ai_response_cache[msg_key]
            if now - timestamp < timedelta(minutes=CACHE_TTL_MINUTES):
                print(f"DEBUG: Cache HIT untuk: {msg_key}")
                return jsonify({'response': cached_reply})

        # Panggil Groq Chat Completions API dengan retry
        import time
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        
        answer = None
        status_code = 500
        
        for attempt in range(3):
            resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            status_code = resp.status_code
            if status_code == 200:
                answer = resp.json()['choices'][0]['message']['content']
                break
            elif status_code == 429:
                time.sleep(3)
                continue
            else:
                print(f"Groq API Error: {resp.status_code} - {resp.text}")
                break
                
        if status_code == 429 and not answer:
            return jsonify({'response': '⏳ Nina sedang beristirahat sejenak karena batasan rate limit Groq. Mohon tunggu beberapa saat lalu coba lagi ya!'}), 429
            
        if not answer:
            return jsonify({'response': f'⚠️ Terjadi gangguan koneksi ke server Groq (Error {status_code}). Coba lagi nanti.'}), 500
        
        # Simpan ke Cache agar pertanyaan sama tidak panggil API lagi
        ai_response_cache[msg_key] = (now, answer)
        return jsonify({'response': answer})
    except Exception as e:
        error_detail = str(e)
        print("Error AI:", error_detail)
        return jsonify({'response': f'⚠️ Error: {error_detail}'}), 500

def ask_nina(user_message):
    """Fungsi inti Nina AI dengan sistem Cache untuk menghemat kuota API (Groq AI)."""
    if not GROQ_API_KEY:
        return '⚠️ API Key Groq belum dikonfigurasi.'
    
    # 1. Cek Cache terlebih dahulu
    msg_key = user_message.lower().strip()
    now = datetime.now()
    
    if msg_key in ai_response_cache:
        timestamp, cached_reply = ai_response_cache[msg_key]
        # Jika cache masih berlaku (kurang dari CACHE_TTL_MINUTES)
        if now - timestamp < timedelta(minutes=CACHE_TTL_MINUTES):
            print(f"DEBUG: Menggunakan CACHE untuk: {msg_key}")
            return cached_reply

    try:
        dashboard_data = fetch_dashboard_data()
        context_lines = []
        for prov in dashboard_data.get('regional_status', []):
            context_lines.append(f"- {prov.get('region')}: Target {prov.get('target')} Ha, Realisasi {prov.get('realized')} Ha (Status: {prov.get('status')})")

        system_prompt = f"""Kamu adalah Nina, Asisten AI ramah dan profesional untuk WebGIS Monev BPLIP1 Makassar.
Tugasmu adalah menjawab pertanyaan pengguna seputar proyek cetak sawah.

Data REAL-TIME saat ini:
- Total Target: {dashboard_data.get('summary', {}).get('total_area_target', 0)} Ha
- Total Realisasi: {dashboard_data.get('summary', {}).get('total_area_realized', 0)} Ha
- Proyek Aktif: {dashboard_data.get('summary', {}).get('active_projects', 0)}

Rincian per provinsi:
{chr(10).join(context_lines)}

Gunakan data di atas untuk menjawab. Jawablah dengan singkat, ramah, dan langsung ke intinya. Jangan mengarang data yang tidak ada."""

        import time
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        
        answer = None
        status_code = 500
        
        for attempt in range(3):
            resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            status_code = resp.status_code
            if status_code == 200:
                answer = resp.json()['choices'][0]['message']['content']
                break
            elif status_code == 429:
                time.sleep(3)
                continue
            else:
                break
        
        if status_code == 429 and not answer:
            return '⏳ Nina sedang istirahat sejenak karena batasan rate limit Groq. Coba lagi dalam beberapa saat ya!'
            
        if not answer:
            return f'⚠️ Gangguan koneksi ke server Groq (Error {status_code}).'
        
        # 2. Simpan ke Cache jika berhasil
        ai_response_cache[msg_key] = (now, answer)
        return answer
        
    except Exception as e:
        return f'⚠️ Error: {str(e)}'


@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    """Endpoint webhook untuk menerima pesan dari Telegram."""
    try:
        data = request.get_json()
        message = data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        user_text = message.get('text', '').strip()

        if not chat_id or not user_text:
            return jsonify({'ok': True})

        # Abaikan command /start
        if user_text == '/start':
            reply = '👋 Halo! Saya *Nina*, Asisten AI BPLIP1 Makassar.\n\nSilakan tanyakan apa saja tentang progres cetak sawah, target luasan, atau status per provinsi!'
        else:
            reply = ask_nina(user_text)

        # Kirim balasan ke Telegram
        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                'chat_id': chat_id,
                'text': reply,
                'parse_mode': 'Markdown'
            },
            timeout=15
        )
        return jsonify({'ok': True})
    except Exception as e:
        print('Telegram webhook error:', str(e))
        return jsonify({'ok': True})


@app.route('/api/set_webhook')
def set_telegram_webhook():
    """Helper untuk mendaftarkan webhook URL ke Telegram (jalankan sekali)."""
    if not TELEGRAM_BOT_TOKEN:
        return jsonify({'error': 'TELEGRAM_BOT_TOKEN belum dikonfigurasi di Vercel'})
    vercel_url = request.host_url.rstrip('/')
    webhook_url = f"{vercel_url}/webhook/telegram"
    resp = requests.post(
        f"{TELEGRAM_API}/setWebhook",
        json={'url': webhook_url},
        timeout=10
    )
    return jsonify({'status': resp.status_code, 'result': resp.json(), 'webhook_url': webhook_url})


if __name__ == '__main__':
    app.run(debug=True)
