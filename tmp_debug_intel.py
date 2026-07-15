import json
import os
import tempfile
from marketing_brain_os.dashboard_repository import DashboardRepository
from marketing_brain_os.dashboard_service import DashboardService
import src.api.app as api_app

temp_dir = tempfile.mkdtemp(prefix='test_api_intel_')
repo = DashboardRepository(data_dir=temp_dir)
service = DashboardService(repo=repo)
api_app.dashboard_service = service
product = {
    'product_id': 'tg-intel-001',
    'listing': {
        'title': 'Samsung Galaxy S23',
        'description': 'Latest Galaxy phone with premium features.',
        'price': {'amount': 1200.0, 'currency': 'USD'},
        'category': 'tech',
    },
    'seller': {'username': 'seller_egy', 'display_name': 'Seller EG'},
    'metadata': {'acquired_at': '2024-07-01T10:00:00Z'},
    'status': 'active',
}
with open(os.path.join(temp_dir, product['product_id'] + '.json'), 'w', encoding='utf-8') as f:
    json.dump(product, f)
app = api_app.app
print('global service type', type(api_app.dashboard_service))
print('newest count', len(api_app.dashboard_service.get_newest_products(1)))
print('newest id', api_app.dashboard_service.get_newest_products(1)[0]['product_id'])
resp = app.test_client().get('/api/intelligence/products/newest?limit=1').get_json()
print('route json', resp)
print('single status', app.test_client().get(f"/api/intelligence/product/{product['product_id']}").status_code)
