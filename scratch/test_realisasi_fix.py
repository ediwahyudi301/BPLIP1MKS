import requests, pandas as pd, io
import sys
import os

sys.path.append(os.getcwd())
from app import get_realisasi_data

print("--- Testing Sulawesi 5 - Minggu 1 ---")
data1 = get_realisasi_data('sulsel_5', 1)
if 'error' in data1:
    print("Error:", data1['error'])
else:
    print("Num Rows:", len(data1['realisasi_data']))
    for i in range(min(5, len(data1['realisasi_data']))):
        print(f"Row {i}:", data1['realisasi_data'][i])

print("\n--- Testing Sulawesi 5 - Minggu 2 ---")
data2 = get_realisasi_data('sulsel_5', 2)
if 'error' in data2:
    print("Error:", data2['error'])
else:
    print("Num Rows:", len(data2['realisasi_data']))
    for i in range(min(5, len(data2['realisasi_data']))):
        print(f"Row {i}:", data2['realisasi_data'][i])
