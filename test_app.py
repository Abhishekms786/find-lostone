import pytest
from app import app, get_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def test_homepage(client):
    """Test that homepage loads successfully with stats and items."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'FindIt' in response.data

def test_browse_page(client):
    """Test browse items page with search, filters, and categories."""
    response = client.get('/browse')
    assert response.status_code == 200
    assert b'Browse' in response.data or b'Items' in response.data

    # Query filter
    response_search = client.get('/browse?q=Wallet')
    assert response_search.status_code == 200
    assert b'Wallet' in response_search.data

    # Type filters
    response_lost = client.get('/browse?type=lost')
    assert response_lost.status_code == 200

    response_found = client.get('/browse?type=found')
    assert response_found.status_code == 200

    # Category filter
    response_cat = client.get('/browse?category=Electronics')
    assert response_cat.status_code == 200

def test_api_stats(client):
    """Test JSON statistics endpoint."""
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert 'total' in data
    assert 'lost' in data
    assert 'found' in data
    assert 'returned' in data

def test_user_registration_flow(client):
    """Test user registration validation and success."""
    # Test validation failure: mismatch passwords
    res_fail = client.post('/register', data={
        'name': 'Test Student',
        'email': 'newstudent@college.edu',
        'password': 'Password123',
        'confirm_password': 'MismatchPassword'
    }, follow_redirects=True)
    assert b'Passwords do not match' in res_fail.data

    # Test registration success
    db = get_db()
    db.users.delete_one({'email': 'newstudent@college.edu'})
    res_success = client.post('/register', data={
        'name': 'Test Student',
        'email': 'newstudent@college.edu',
        'password': 'Password123',
        'confirm_password': 'Password123'
    }, follow_redirects=True)
    assert res_success.status_code == 200
    assert b'Welcome, Test Student' in res_success.data

def test_login_logout_flow(client):
    """Test authenticating a user and logging out."""
    res_login = client.post('/login', data={
        'email': 'alice@college.edu',
        'password': 'Password1'
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b'alice@college.edu' in res_login.data or b'Dashboard' in res_login.data or b'Alice' in res_login.data

    # Check dashboard is accessible
    res_dash = client.get('/dashboard')
    assert res_dash.status_code == 200

    # Logout
    res_logout = client.get('/logout', follow_redirects=True)
    assert res_logout.status_code == 200

def test_create_and_manage_item(client):
    """Test logged in student creating an item and viewing its details."""
    # Login as Alice
    client.post('/login', data={
        'email': 'alice@college.edu',
        'password': 'Password1'
    }, follow_redirects=True)

    # Post new lost item
    res_create = client.post('/items/create', data={
        'title': 'Lost Calculus Notebook',
        'description': 'Green spiral notebook left in Lab Block 302',
        'type': 'lost',
        'category': 'Books and Notes',
        'location': 'Lab Block',
        'date_lost_found': '2026-10-30',
        'contact_email': 'alice@college.edu',
        'contact_phone': '9876543210',
        'image_url': ''
    }, follow_redirects=True)
    assert res_create.status_code == 200

    # Verify item exists in database and browse
    db = get_db()
    created_item = db.items.find_one({'title': 'Lost Calculus Notebook'})
    assert created_item is not None
    item_id = str(created_item['_id'])

    # View details
    res_detail = client.get(f'/item/{item_id}')
    assert res_detail.status_code == 200
    assert b'Calculus Notebook' in res_detail.data

def test_claim_flow(client):
    """Test claim submission from one user to another."""
    db = get_db()
    # Find Bob's item or create one
    found_item = db.items.find_one({'type': 'found', 'status': 'active'})
    assert found_item is not None
    item_id = str(found_item['_id'])

    # Login as Alice
    client.post('/login', data={
        'email': 'alice@college.edu',
        'password': 'Password1'
    }, follow_redirects=True)

    # Alice submits claim on Bob's found item
    res_claim = client.post(f'/items/{item_id}/claim', data={
        'message': 'This matches my lost belongings! I have the serial number.'
    }, follow_redirects=True)
    assert res_claim.status_code == 200
    assert b'Claim submitted' in res_claim.data or b'claim' in res_claim.data.lower()

def test_admin_portal_flow(client):
    """Test admin authentication and controls."""
    get_db()
    res_login = client.post('/login', data={
        'email': 'admin@findit.edu',
        'password': 'Admin@1234'
    }, follow_redirects=True)
    assert res_login.status_code == 200

    res_admin = client.get('/admin')
    assert res_admin.status_code == 200
    assert b'Admin' in res_admin.data
    assert b'System Overview' in res_admin.data or b'Dashboard' in res_admin.data or b'Statistics' in res_admin.data
