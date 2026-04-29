from flask import Flask, render_template, jsonify, request

import pandas as pd
import requests
import io

app = Flask(__name__)

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1b8XGbfCcCshv9MXfdQ8sHR5KfiT-l6zBf39YcrvicmJccREctopoq79hCEfzq5hnya_hM_LxtwML/pub?gid=684955607&single=true&output=csv"

# Pemetaan (Mapping) Paket ke ID Folder Google Drive
# Anda perlu mengganti ID di bawah ini dengan ID folder spesifik jika Anda ingin 
# menu laporan langsung terbuka di dalam sub-folder yang bersangkutan.
# Default: 1HCmAUjk0Yd4O4OzQXQ2jEIXDIaaLq2RO (Folder Utama)
DRIVE_FOLDER_MAPPING = {
    'sulsel_1': '1HCmAUjk0Yd4O4OzQXQ2jEIXDIaaLq2RO', # Ganti dengan ID folder Paket Sulsel 1
    # Tambahkan mapping untuk paket lain di sini (misal: 'sulsel_2': 'ID_FOLDER_NYA')
}

def fetch_dashboard_data():
    try:
        req = requests.get(SHEET_CSV_URL)
        req.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(req.text))
        
        regional_status = []
        total_target = 0
        total_realized = 0
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
                    
                total_target += target_val
                
                current_region = no_val.title()
                region_data = {
                    'region': current_region,
                    'target': target_val,
                    'realized': 0, 
                    'status': 'Persiapan'
                }
            else:
                # Menghitung Baris Paket Proyek Aktif
                active_projects += 1
                
                # Logika Status Penayangan berdasarkan Kesimpulan
                kesimpulan = str(row['Kesimpulan']).strip().lower()
                if ('tayang' in kesimpulan) or ('lelang' in kesimpulan) or ('evaluasi' in kesimpulan):
                    if region_data and region_data['status'] == 'Persiapan':
                        region_data['status'] = 'Penayangan'
                        
                # Menghitung realisasi (jika ada data kedepannya)
                # Contoh: saat ini data 'realized' di sheet memang belum ada representasi eksplisit
                
        # Menambahkan data wilayah terakhir ke array
        if region_data:
            regional_status.append(region_data)
            
        overall_progress = 0
        if total_target > 0:
            overall_progress = round((total_realized / total_target) * 100, 1)
            
        return {
            'summary': {
                'total_area_target': total_target, 
                'total_area_realized': total_realized,
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
    except Exception as e:
        print("Error fetching data dari API:", e)
        # Fallback jika terjadi kesalahan koneksi
        return {
            'summary': { 'total_area_target': 12599.05, 'total_area_realized': 0, 'active_projects': 35, 'overall_progress': 0 },
            'monthly_progress': { 'labels': ['Jan'], 'target': [0], 'realized': [0] },
            'regional_status': [ {'region': 'Koneksi Gagal', 'target': 0, 'realized': 0, 'status': 'Error'} ]
        }

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

@app.route('/api/data')
def get_data():
    return jsonify(fetch_dashboard_data())

@app.route('/api/kurva_s/<paket_id>')
def get_kurva_s(paket_id):
    # Mapping paket_id to sheet name, default to PAKET_SULSEL1
    sheet_name = 'PAKET_SULSEL1'
    if paket_id.startswith('sulsel_'):
        nomor = paket_id.split('_')[1]
        sheet_name = f'PAKET_SULSEL{nomor}'
    
    url = f"https://docs.google.com/spreadsheets/d/1fPOem8nUIiQlhYbnZBDPafutAeaUMkKZBO6_0zRAqoQ/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        req = requests.get(url)
        req.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(req.text))
        
        target_weekly = []
        realized_weekly = []
        
        for index, row in df.iterrows():
            row_str = row.astype(str).str.upper()
            
            # Find the row containing weekly targets
            if any("KOMULATIF RENCANA" in str(cell) for cell in row_str):
                for val in row:
                    try:
                        num = float(str(val).replace(',', '.'))
                        if pd.notna(num):
                            target_weekly.append(num)
                    except ValueError:
                        pass
                        
            # Find the row containing weekly actuals
            if any(str(cell).strip() == "REALISASI" for cell in row_str):
                for val in row:
                    try:
                        num = float(str(val).replace(',', '.'))
                        if pd.notna(num):
                            realized_weekly.append(num)
                    except ValueError:
                        pass
        
        # Calculate cumulative values
        target_cumulative = []
        current_target = 0
        for val in target_weekly:
            current_target += val
            target_cumulative.append(round(current_target, 2))
            
        realized_cumulative = []
        current_realized = 0
        for val in realized_weekly:
            current_realized += val
            realized_cumulative.append(round(current_realized, 2))
            
        deviation = []
        for i in range(len(realized_cumulative)):
            if i < len(target_cumulative):
                dev = round(realized_cumulative[i] - target_cumulative[i], 2)
                deviation.append(dev)
            
        labels = [f"M{i+1}" for i in range(len(target_cumulative))]
        
        return jsonify({
            'labels': labels,
            'target': target_cumulative,
            'realized': realized_cumulative,
            'deviation': deviation
        })
    except Exception as e:
        print("Error fetching S-Curve data:", e)
        return jsonify({
            'labels': [],
            'target': [],
            'realized': [],
            'error': str(e)
        }), 500

@app.route('/laporan')
def laporan():
    paket = request.args.get('paket', 'sulsel_1')
    
    # Ambil ID folder dari dictionary, jika tidak ada fallback ke folder utama
    folder_id = DRIVE_FOLDER_MAPPING.get(paket, '1HCmAUjk0Yd4O4OzQXQ2jEIXDIaaLq2RO')
    
    return render_template('laporan.html', paket=paket, folder_id=folder_id)

if __name__ == '__main__':
    app.run(debug=True)
