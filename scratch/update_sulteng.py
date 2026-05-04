import glob, re

insert_str = '''
                        <!-- Master Link for Sulteng -->
                        <div class="mb-2">
                            <a href="{{ url_for('master_sulteng') }}" class="flex items-center py-2 px-3 bg-emerald-500/10 text-emerald-400 rounded-lg text-xs font-bold transition hover:bg-emerald-500/20">
                                <i class="fa-solid fa-table-list mr-2"></i>
                                MASTER PAKET SULTENG
                            </a>
                        </div>
'''

templates = glob.glob('templates/*.html')
for t in templates:
    with open(t, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = re.sub(r'(id="dropdown-sulteng"[^>]*>)(\s*{%\s*for i in range\(1,\s*12\)\s*%})', r'\1' + insert_str + r'\2', content)
    
    if new_content != content:
        with open(t, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {t}")
