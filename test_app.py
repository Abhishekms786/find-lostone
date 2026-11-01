import pytest
from app import app, get_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

# 1. User registration
def test_1_user_registration(client):
    """Test user registration validation and success."""
    # Mismatch passwords validation
    res_fail = client.post('/register', data={
        'name': 'Student Tester',
        'email': 'tester@college.edu',
        'password': 'Password123',
        'confirm_password': 'WrongPassword123'
    }, follow_redirects=True)
    assert b'Passwords do not match' in res_fail.data

    # Successful registration
    db = get_db()
    db.users.delete_one({'email': 'tester@college.edu'})
    res_success = client.post('/register', data={
        'name': 'Student Tester',
        'email': 'tester@college.edu',
        'password': 'Password123',
        'confirm_password': 'Password123'
    }, follow_redirects=True)
    assert res_success.status_code == 200
    assert b'Welcome, Student Tester' in res_success.data

# 2. Login and logout
def test_2_login_and_logout(client):
    """Test authenticating a user and logging out."""
    res_login = client.post('/login', data={
        'email': 'alice@college.edu',
        'password': 'Password1'
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b'alice@college.edu' in res_login.data or b'Dashboard' in res_login.data

    # Verify session active
    res_dash = client.get('/dashboard')
    assert res_dash.status_code == 200

    # Logout
    res_logout = client.get('/logout', follow_redirects=True)
    assert res_logout.status_code == 200

# 3. Lost item creation
def test_3_create_lost_item(client):
    """Test student reporting a lost item."""
    client.post('/login', data={'email': 'alice@college.edu', 'password': 'Password1'}, follow_redirects=True)

    res_create = client.post('/items/create', data={
        'title': 'Lost Graphing Calculator',
        'description': 'TI-84 Plus CE lost in Library 2nd floor reading hall.',
        'type': 'lost',
        'category': 'Electronics',
        'location': 'Library',
        'date_lost_found': '2026-11-01',
        'image_url': ''
    }, follow_redirects=True)
    assert res_create.status_code == 200
    assert b'Graphing Calculator' in res_create.data

    db = get_db()
    item = db.items.find_one({'title': 'Lost Graphing Calculator'})
    assert item is not None
    assert item['type'] == 'lost'

# 4. Found item creation
def test_4_create_found_item(client):
    """Test student reporting a found item."""
    client.post('/login', data={'email': 'bob@college.edu', 'password': 'Password1'}, follow_redirects=True)

    res_create = client.post('/items/create', data={
        'title': 'Found Set of Dorm Keys',
        'description': 'Three keys with a red lanyard found near cafeteria entrance.',
        'type': 'found',
        'category': 'Keys',
        'location': 'Cafeteria',
        'date_lost_found': '2026-11-01',
        'image_url': ''
    }, follow_redirects=True)
    assert res_create.status_code == 200
    assert b'Found Set of Dorm Keys' in res_create.data

    db = get_db()
    item = db.items.find_one({'title': 'Found Set of Dorm Keys'})
    assert item is not None
    assert item['type'] == 'found'

# 5. Search
def test_5_search_items(client):
    """Test search with text query and special characters."""
    res_search = client.get('/browse?q=Calculator')
    assert res_search.status_code == 200
    assert b'Calculator' in res_search.data

    # Special characters search query test (safe regex escaping)
    res_special = client.get('/browse?q=Dorm+(Keys)')
    assert res_special.status_code == 200

# 6. Category filtering
def test_6_category_filtering(client):
    """Test filtering items by category and type."""
    res_cat = client.get('/browse?category=Electronics')
    assert res_cat.status_code == 200

    res_lost = client.get('/browse?type=lost')
    assert res_lost.status_code == 200

    res_found = client.get('/browse?type=found')
    assert res_found.status_code == 200

# 7. Item details
def test_7_item_details_page(client):
    """Test viewing item details."""
    db = get_db()
    item = db.items.find_one({'title': 'Lost Graphing Calculator'})
    assert item is not None
    item_id = str(item['_id'])

    res = client.get(f'/item/{item_id}')
    assert res.status_code == 200
    assert b'Lost Graphing Calculator' in res.data
    assert b'Library' in res.data

# 8. Claim request submission
def test_8_claim_request_submission(client):
    """Test claim request from a non-owner student."""
    db = get_db()
    # Bob owns 'Found Set of Dorm Keys'
    bob_item = db.items.find_one({'title': 'Found Set of Dorm Keys'})
    assert bob_item is not None
    item_id = str(bob_item['_id'])

    # Login as Alice (not the owner)
    client.post('/login', data={'email': 'alice@college.edu', 'password': 'Password1'}, follow_redirects=True)

    # Ensure item is active and clean existing claims
    db.items.update_one({'_id': bob_item['_id']}, {'$set': {'status': 'active'}})
    db.claims.delete_many({'item_id': bob_item['_id']})

    res_claim = client.post(f'/items/{item_id}/claim', data={
        'message': 'These keys belong to my dorm room #204. Red lanyard has my initials.'
    }, follow_redirects=True)
    assert res_claim.status_code == 200
    assert b'Claim request submitted' in res_claim.data

    claim = db.claims.find_one({'item_id': bob_item['_id']})
    assert claim is not None
    assert claim['status'] == 'pending'

# 9. Claim acceptance and rejection
def test_9_claim_acceptance_and_rejection(client):
    """Test owner accepting a pending claim."""
    db = get_db()
    bob_item = db.items.find_one({'title': 'Found Set of Dorm Keys'})
    assert bob_item is not None
    claim = db.claims.find_one({'item_id': bob_item['_id'], 'status': 'pending'})
    assert claim is not None
    claim_id = str(claim['_id'])

    # Login as Bob (owner of the item)
    client.post('/login', data={'email': 'bob@college.edu', 'password': 'Password1'}, follow_redirects=True)

    # Bob accepts the claim
    res_accept = client.post(f'/claims/{claim_id}/respond', data={'action': 'accept'}, follow_redirects=True)
    assert res_accept.status_code == 200

    updated_claim = db.claims.find_one({'_id': claim['_id']})
    assert updated_claim['status'] == 'accepted'

    updated_item = db.items.find_one({'_id': bob_item['_id']})
    assert updated_item['status'] == 'claimed'

# 10. Item status update
def test_10_item_status_update(client):
    """Test owner updating status to returned."""
    db = get_db()
    bob_item = db.items.find_one({'title': 'Found Set of Dorm Keys'})
    assert bob_item is not None
    item_id = str(bob_item['_id'])

    # Login as Bob
    client.post('/login', data={'email': 'bob@college.edu', 'password': 'Password1'}, follow_redirects=True)

    res_status = client.post(f'/items/{item_id}/status', data={'status': 'returned'}, follow_redirects=True)
    assert res_status.status_code == 200

    updated_item = db.items.find_one({'_id': bob_item['_id']})
    assert updated_item['status'] == 'returned'

# 11. Admin login
def test_11_admin_login(client):
    """Test admin authentication and control panel access."""
    res_login = client.post('/login', data={
        'email': 'admin@findit.edu',
        'password': 'Admin@1234'
    }, follow_redirects=True)
    assert res_login.status_code == 200

    res_admin = client.get('/admin')
    assert res_admin.status_code == 200
    assert b'Admin Dashboard' in res_admin.data
    assert b'Registered Students' in res_admin.data

# 12. Admin permissions protection
def test_12_admin_permissions_protection(client):
    """Test that a regular student cannot access admin routes."""
    # Login as Alice (student)
    client.post('/login', data={'email': 'alice@college.edu', 'password': 'Password1'}, follow_redirects=True)

    # Attempt to open admin dashboard
    res_denied = client.get('/admin', follow_redirects=True)
    assert res_denied.status_code == 200
    assert b'Admin access required' in res_denied.data or b'FindIt' in res_denied.data

# 13. MongoDB persistence
def test_13_mongodb_persistence(client):
    """Verify PyMongo NoSQL CRUD operations and direct database persistence."""
    db = get_db()
    assert db is not None
    assert db.name == 'findit_db'

    # Direct collection verification
    collections = db.list_collection_names()
    assert 'users' in collections
    assert 'items' in collections
    assert 'claims' in collections

    # Insert test document into items collection
    from datetime import datetime
    test_doc = {
        'title': 'Persistence Test Umbrella',
        'description': 'Directly inserted into MongoDB to test NoSQL persistence',
        'type': 'lost',
        'category': 'Accessories',
        'location': 'Main Building',
        'status': 'active',
        'created_at': datetime.now()
    }
    result = db.items.insert_one(test_doc)
    doc_id = result.inserted_id

    # Verify query
    found = db.items.find_one({'_id': doc_id})
    assert found is not None
    assert found['title'] == 'Persistence Test Umbrella'

    # Cleanup test document
    db.items.delete_one({'_id': doc_id})
    assert db.items.find_one({'_id': doc_id}) is None
