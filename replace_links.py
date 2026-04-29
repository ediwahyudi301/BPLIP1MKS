import glob

for filename in ['templates/index.html', 'templates/peta.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace("url_for(\\'laporan\\')", "url_for('laporan')")
    content = content.replace("url_for(\\'kurva_s\\')", "url_for('kurva_s')")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
