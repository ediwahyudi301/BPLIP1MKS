import requests, pandas as pd, io
import sys
import os

sys.path.append(os.getcwd())
from app import get_realisasi_data

print("--- Testing Sulawesi 5 - Minggu 1 ---")
# Add a monkeypatch to print indices during get_realisasi_data
import app
original_get_realisasi_data = app.get_realisasi_data

def patched_get_realisasi_data(paket_id, minggu=1):
    # I'll just look at the output of the actual function
    return original_get_realisasi_data(paket_id, minggu)

data1 = get_realisasi_data('sulsel_5', 1)
if 'error' in data1:
    print("Error:", data1['error'])
else:
    for i, item in enumerate(data1['realisasi_data']):
        if item['no'] == '1':
            print(f"Item No 1: {item}")
