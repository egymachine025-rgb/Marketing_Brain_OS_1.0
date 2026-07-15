import json
from pathlib import Path

products = list(Path('data/products').glob('*.json'))
print(f'Total products: {len(products)}')

for p in products[:5]:
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
        ch = d.get('source', {}).get('channel', 'no channel')
        print(f'  - {p.name}: {ch}')