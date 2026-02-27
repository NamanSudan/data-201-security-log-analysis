import json

for nb in ['notebooks/02_explore_apache_error.ipynb', 'notebooks/03_explore_apache_error.ipynb']:
    with open(nb, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    code_cells = [c for c in data['cells'] if c['cell_type'] == 'code']
    cell = code_cells[1]  # cell 2 (0-indexed)
    source = ''.join(cell['source'])
    
    source = source.replace(
        "if 'line' in c_low: mapping = 'event_id'",
        "if 'line' in c_low:\n            mapping = 'event_id'"
    ).replace(
        "elif 'labels' in c_low: mapping = 'http_event_category'",
        "elif 'labels' in c_low:\n            mapping = 'http_event_category'"
    ).replace(
        "elif 'rules' in c_low: mapping = 'http_signature_matches'",
        "elif 'rules' in c_low:\n            mapping = 'http_signature_matches'"
    )
    
    cell['source'] = [line + '\n' for line in source.split('\n')]
    
    with open(nb, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1)
    print(f'Fixed {nb}')
