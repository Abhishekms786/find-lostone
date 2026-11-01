import os
import sys
import re

# Ensure Windows terminal doesn't crash on unicode console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from datetime import datetime, timedelta
from functools import wraps
from bson import ObjectId
from bson.errors import InvalidId
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, session, jsonify, abort)
from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# ---------------------------------------------
# Configuration
# ---------------------------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.permanent_session_lifetime = timedelta(days=7)

try:
    import certifi
    CA_FILE = certifi.where()
except ImportError:
    CA_FILE = None

import time

# ---------------------------------------------
# MongoDB Connection
# ---------------------------------------------
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME   = os.environ.get('DB_NAME', 'findit_db')

client = None
db     = None
db_error_message = None
_last_attempt_time = 0.0
_RETRY_INTERVAL = 10.0  # seconds between reconnect attempts on failure

def get_db():
    """Return the database handle, connecting lazily with cooldown on failure."""
    global client, db, db_error_message, _last_attempt_time
    if db is not None:
        return db

    now = time.time()
    # If connection previously failed, wait before retrying to prevent blocking Gunicorn workers
    if (now - _last_attempt_time) < _RETRY_INTERVAL:
        return None

    _last_attempt_time = now
    try:
        mongo_kwargs = {
            'serverSelectionTimeoutMS': 3500,
            'connectTimeoutMS': 3500,
            'socketTimeoutMS': 3500,
        }
        if CA_FILE and ('mongodb+srv://' in MONGO_URI or 'tls=true' in MONGO_URI.lower() or 'ssl=true' in MONGO_URI.lower()):
            mongo_kwargs['tlsCAFile'] = CA_FILE

        client = MongoClient(MONGO_URI, **mongo_kwargs)
        # Verify server responsiveness (works for local MongoDB and Atlas)
        client.admin.command('ping')
        db = client[DB_NAME]
        _create_indexes(db)
        _seed_admin(db)
        db_error_message = None
        # Mask any passwords in MONGO_URI for secure logging
        safe_uri = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', MONGO_URI)
        is_cloud = MONGO_URI.startswith('mongodb+srv://')
        db_type = 'MongoDB Atlas Cloud' if is_cloud else 'Local MongoDB'
        print(f"[FindIt] Connected to {db_type} ({safe_uri}) -> database: {DB_NAME}")
    except Exception as exc:
        db_error_message = str(exc)
        safe_uri = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', MONGO_URI)
        print(f"[FindIt] MongoDB connection failed for {safe_uri}: {exc}")
        db = None
    return db


def _create_indexes(database):
    """Create indexes once on first connect."""
    database.users.create_index('email', unique=True)
    database.items.create_index([('status', ASCENDING)])
    database.items.create_index([('type', ASCENDING)])
    database.items.create_index([('category', ASCENDING)])
    database.items.create_index([('created_at', DESCENDING)])
    database.claims.create_index([('item_id', ASCENDING), ('requester_id', ASCENDING)])


def _seed_admin(database):
    """Insert first admin from env vars if none exists."""
    admin_email    = os.environ.get('ADMIN_EMAIL', 'admin@findit.edu')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@1234')
    if not database.users.find_one({'role': 'admin'}):
        database.users.insert_one({
            'name'         : 'Administrator',
            'email'        : admin_email,
            'password_hash': generate_password_hash(admin_password),
            'role'         : 'admin',
            'created_at'   : datetime.utcnow(),
        })
        print(f"[FindIt] Admin account created -> {admin_email}")


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
CATEGORIES = [
    'Electronics', 'Mobile Phones', 'Wallets', 'Identity Cards',
    'Books and Notes', 'Bags', 'Keys', 'Accessories', 'Clothing', 'Other'
]

LOCATIONS = [
    'Main Building', 'Library', 'Cafeteria', 'Sports Complex',
    'Lab Block', 'Hostel A', 'Hostel B', 'Parking Area',
    'Auditorium', 'Admin Block', 'Other'
]

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def oid(s):
    """Convert string to ObjectId, returning None on failure."""
    try:
        return ObjectId(s)
    except (InvalidId, TypeError):
        return None


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    database = get_db()
    if database is None:
        return None
    return database.users.find_one({'_id': oid(uid)})


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = current_user()
        if not user or user.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


def db_required(f):
    """Decorator that aborts with 503 when MongoDB is unreachable."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if get_db() is None:
            err = db_error_message or "Connection failed"
            return render_template(
                'error.html',
                message=f'MongoDB is currently unreachable ({err}). Please ensure your MongoDB instance is running or verify MONGO_URI in your .env file.'
            ), 503
        return f(*args, **kwargs)
    return decorated


def paginate(query_cursor, page, per_page=9):
    total  = query_cursor.count()
    items  = list(query_cursor.skip((page - 1) * per_page).limit(per_page))
    pages  = (total + per_page - 1) // per_page
    return items, total, pages


def validate_email(email):
    return re.match(r'^[\w\.\+\-]+@[\w\-]+\.[\w\.]+$', email)


def validate_password(pw):
    """Min 8 chars, at least one digit and one letter."""
    return len(pw) >= 8 and any(c.isdigit() for c in pw) and any(c.isalpha() for c in pw)


# ─────────────────────────────────────────────
# Context processor
# ─────────────────────────────────────────────
@app.context_processor
def inject_user():
    return {'current_user': current_user(), 'categories': CATEGORIES, 'locations': LOCATIONS}


# ─────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', message='403 - Forbidden'), 403


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='500 - Internal Server Error'), 500


# ─────────────────────────────────────────────
# PUBLIC ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def index():
    database = get_db()
    recent_lost  = []
    recent_found = []
    stats        = {'total': 0, 'lost': 0, 'found': 0, 'returned': 0}

    if database is not None:
        recent_lost  = list(database.items.find({'type': 'lost',  'status': 'active'})
                            .sort('created_at', DESCENDING).limit(6))
        recent_found = list(database.items.find({'type': 'found', 'status': 'active'})
                            .sort('created_at', DESCENDING).limit(6))
        stats['total']    = database.items.count_documents({})
        stats['lost']     = database.items.count_documents({'type': 'lost'})
        stats['found']    = database.items.count_documents({'type': 'found'})
        stats['returned'] = database.items.count_documents({'status': 'returned'})

    return render_template('index.html',
                           recent_lost=recent_lost,
                           recent_found=recent_found,
                           stats=stats)


@app.route('/browse')
def browse():
    database = get_db()
    if database is None:
        return render_template('browse.html', items=[], total=0, pages=1,
                               page=1, q='', item_type='', category='', location='', sort='newest')

    q         = request.args.get('q', '').strip()
    item_type = request.args.get('type', '')
    category  = request.args.get('category', '')
    location  = request.args.get('location', '')
    sort      = request.args.get('sort', 'newest')
    page      = max(1, int(request.args.get('page', 1)))

    query = {'status': {'$ne': 'deleted'}}
    if q:
        safe_q = re.escape(q)
        query['$or'] = [
            {'title'      : {'$regex': safe_q, '$options': 'i'}},
            {'description': {'$regex': safe_q, '$options': 'i'}},
        ]
    if item_type in ('lost', 'found'):
        query['type'] = item_type
    if category:
        query['category'] = category
    if location:
        query['location'] = location

    sort_order = DESCENDING if sort == 'newest' else ASCENDING
    cursor = database.items.find(query).sort('created_at', sort_order)

    total  = database.items.count_documents(query)
    per_page = 9
    items  = list(cursor.skip((page - 1) * per_page).limit(per_page))
    pages  = max(1, (total + per_page - 1) // per_page)

    return render_template('browse.html',
                           items=items, total=total, pages=pages, page=page,
                           q=q, item_type=item_type, category=category,
                           location=location, sort=sort)


@app.route('/item/<item_id>')
def item_details(item_id):
    database = get_db()
    if database is None:
        abort(503)

    item = database.items.find_one({'_id': oid(item_id)})
    if not item:
        abort(404)

    owner   = database.users.find_one({'_id': item['created_by']})
    claims  = list(database.claims.find({'item_id': item['_id']}).sort('created_at', DESCENDING))

    # Attach requester info to each claim
    for claim in claims:
        claim['requester'] = database.users.find_one({'_id': claim['requester_id']})

    user = current_user()
    user_claim = None
    if user:
        user_claim = database.claims.find_one({
            'item_id'     : item['_id'],
            'requester_id': user['_id'],
        })

    return render_template('item_details.html',
                           item=item, owner=owner, claims=claims,
                           user_claim=user_claim)


# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not validate_email(email):
            errors.append('Invalid email address.')
        if not validate_password(password):
            errors.append('Password must be at least 8 characters with letters and numbers.')
        if password != confirm:
            errors.append('Passwords do not match.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html', name=name, email=email)

        database = get_db()
        if database is None:
            flash('Database unavailable. Try again later.', 'danger')
            return render_template('register.html', name=name, email=email)

        try:
            result = database.users.insert_one({
                'name'         : name,
                'email'        : email,
                'password_hash': generate_password_hash(password),
                'role'         : 'student',
                'created_at'   : datetime.utcnow(),
            })
            session.permanent = True
            session['user_id'] = str(result.inserted_id)
            flash(f'Welcome, {name}! Your account has been created.', 'success')
            return redirect(url_for('dashboard'))
        except DuplicateKeyError:
            flash('An account with that email already exists.', 'danger')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        database = get_db()
        if database is None:
            flash('Database unavailable. Try again later.', 'danger')
            return render_template('login.html', email=email)

        user = database.users.find_one({'email': email})
        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True
            session['user_id'] = str(user['_id'])
            flash(f'Welcome back, {user["name"]}!', 'success')
            next_url = request.args.get('next') or (
                url_for('admin_dashboard') if user['role'] == 'admin' else url_for('dashboard')
            )
            return redirect(next_url)
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ─────────────────────────────────────────────
# STUDENT DASHBOARD ROUTES
# ─────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    user     = current_user()
    database = get_db()
    if database is None:
        return render_template('dashboard.html', my_items=[], my_claims=[], incoming_claims=[])

    my_items = list(database.items.find({'created_by': user['_id']}).sort('created_at', DESCENDING))

    # Claims I made
    my_claims_raw = list(database.claims.find({'requester_id': user['_id']}).sort('created_at', DESCENDING))
    my_claims = []
    for claim in my_claims_raw:
        item = database.items.find_one({'_id': claim['item_id']})
        if item:
            claim['item'] = item
            my_claims.append(claim)

    # Claims others made on my items
    my_item_ids = [i['_id'] for i in my_items]
    incoming_raw = list(database.claims.find({'item_id': {'$in': my_item_ids}}).sort('created_at', DESCENDING))
    incoming_claims = []
    for claim in incoming_raw:
        item      = database.items.find_one({'_id': claim['item_id']})
        requester = database.users.find_one({'_id': claim['requester_id']})
        if item and requester:
            claim['item']      = item
            claim['requester'] = requester
            incoming_claims.append(claim)

    return render_template('dashboard.html',
                           my_items=my_items,
                           my_claims=my_claims,
                           incoming_claims=incoming_claims)


@app.route('/items/create', methods=['GET', 'POST'])
@login_required
@db_required
def create_item():
    if request.method == 'POST':
        user     = current_user()
        database = get_db()
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        item_type   = request.form.get('type', 'lost')
        category    = request.form.get('category', 'Other')
        location    = request.form.get('location', 'Other')
        date_str    = request.form.get('date_lost_found', '')
        image_url   = request.form.get('image_url', '').strip()

        errors = []
        if not title or len(title) < 3:
            errors.append('Title must be at least 3 characters.')
        if not description or len(description) < 10:
            errors.append('Description must be at least 10 characters.')
        if item_type not in ('lost', 'found'):
            errors.append('Invalid item type.')
        if category not in CATEGORIES:
            errors.append('Invalid category.')
        if location not in LOCATIONS:
            errors.append('Invalid location.')

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
        except ValueError:
            date_obj = datetime.utcnow()

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('create_item.html',
                                   form_data=request.form)

        result = database.items.insert_one({
            'title'          : title,
            'description'    : description,
            'type'           : item_type,
            'category'       : category,
            'location'       : location,
            'date_lost_found': date_obj,
            'image_url'      : image_url,
            'status'         : 'active',
            'created_by'     : user['_id'],
            'created_at'     : datetime.utcnow(),
            'updated_at'     : datetime.utcnow(),
        })
        flash('Item reported successfully!', 'success')
        return redirect(url_for('item_details', item_id=str(result.inserted_id)))

    return render_template('create_item.html', form_data={})


@app.route('/items/<item_id>/edit', methods=['GET', 'POST'])
@login_required
@db_required
def edit_item(item_id):
    user     = current_user()
    database = get_db()
    item     = database.items.find_one({'_id': oid(item_id)})

    if not item:
        abort(404)
    if str(item['created_by']) != str(user['_id']) and user.get('role') != 'admin':
        flash('You can only edit your own items.', 'danger')
        return redirect(url_for('item_details', item_id=item_id))

    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        item_type   = request.form.get('type', 'lost')
        category    = request.form.get('category', 'Other')
        location    = request.form.get('location', 'Other')
        date_str    = request.form.get('date_lost_found', '')
        image_url   = request.form.get('image_url', '').strip()

        errors = []
        if not title or len(title) < 3:
            errors.append('Title must be at least 3 characters.')
        if not description or len(description) < 10:
            errors.append('Description must be at least 10 characters.')

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d') if date_str else item['date_lost_found']
        except ValueError:
            date_obj = item['date_lost_found']

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('edit_item.html', item=item, form_data=request.form)

        database.items.update_one({'_id': item['_id']}, {'$set': {
            'title'          : title,
            'description'    : description,
            'type'           : item_type,
            'category'       : category,
            'location'       : location,
            'date_lost_found': date_obj,
            'image_url'      : image_url,
            'updated_at'     : datetime.utcnow(),
        }})
        flash('Item updated successfully!', 'success')
        return redirect(url_for('item_details', item_id=item_id))

    return render_template('edit_item.html', item=item, form_data={})


@app.route('/items/<item_id>/delete', methods=['POST'])
@login_required
@db_required
def delete_item(item_id):
    user     = current_user()
    database = get_db()
    item     = database.items.find_one({'_id': oid(item_id)})

    if not item:
        abort(404)
    if str(item['created_by']) != str(user['_id']) and user.get('role') != 'admin':
        flash('You can only delete your own items.', 'danger')
        return redirect(url_for('item_details', item_id=item_id))

    database.items.delete_one({'_id': item['_id']})
    database.claims.delete_many({'item_id': item['_id']})
    flash('Item deleted.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/items/<item_id>/status', methods=['POST'])
@login_required
@db_required
def update_item_status(item_id):
    user     = current_user()
    database = get_db()
    item     = database.items.find_one({'_id': oid(item_id)})

    if not item:
        abort(404)
    if str(item['created_by']) != str(user['_id']) and user.get('role') != 'admin':
        abort(403)

    new_status = request.form.get('status')
    if new_status in ('active', 'claimed', 'returned'):
        database.items.update_one({'_id': item['_id']}, {'$set': {
            'status'    : new_status,
            'updated_at': datetime.utcnow(),
        }})
        flash(f'Item marked as {new_status}.', 'success')

    return redirect(url_for('item_details', item_id=item_id))


# ─────────────────────────────────────────────
# CLAIM ROUTES
# ─────────────────────────────────────────────

@app.route('/items/<item_id>/claim', methods=['POST'])
@login_required
@db_required
def submit_claim(item_id):
    user     = current_user()
    database = get_db()
    item     = database.items.find_one({'_id': oid(item_id)})

    if not item:
        abort(404)

    if str(item['created_by']) == str(user['_id']):
        flash('You cannot claim your own item.', 'warning')
        return redirect(url_for('item_details', item_id=item_id))

    if item['status'] != 'active':
        flash('This item is no longer available to claim.', 'warning')
        return redirect(url_for('item_details', item_id=item_id))

    existing = database.claims.find_one({
        'item_id'     : item['_id'],
        'requester_id': user['_id'],
        'status'      : 'pending',
    })
    if existing:
        flash('You already have a pending claim on this item.', 'warning')
        return redirect(url_for('item_details', item_id=item_id))

    message = request.form.get('message', '').strip()
    if not message or len(message) < 5:
        flash('Please provide a message with at least 5 characters.', 'danger')
        return redirect(url_for('item_details', item_id=item_id))

    database.claims.insert_one({
        'item_id'     : item['_id'],
        'requester_id': user['_id'],
        'message'     : message,
        'status'      : 'pending',
        'created_at'  : datetime.utcnow(),
    })
    flash('Claim request submitted! The owner will review it.', 'success')
    return redirect(url_for('item_details', item_id=item_id))


@app.route('/claims/<claim_id>/respond', methods=['POST'])
@login_required
@db_required
def respond_claim(claim_id):
    user     = current_user()
    database = get_db()
    claim    = database.claims.find_one({'_id': oid(claim_id)})

    if not claim:
        abort(404)

    item = database.items.find_one({'_id': claim['item_id']})
    if not item:
        abort(404)

    if str(item['created_by']) != str(user['_id']) and user.get('role') != 'admin':
        abort(403)

    action = request.form.get('action')
    if action == 'accept':
        database.claims.update_one({'_id': claim['_id']}, {'$set': {'status': 'accepted'}})
        database.items.update_one({'_id': item['_id']}, {'$set': {
            'status'    : 'claimed',
            'updated_at': datetime.utcnow(),
        }})
        # Reject all other pending claims for this item
        database.claims.update_many(
            {'item_id': item['_id'], '_id': {'$ne': claim['_id']}, 'status': 'pending'},
            {'$set': {'status': 'rejected'}}
        )
        flash('Claim accepted! Item marked as Claimed.', 'success')
    elif action == 'reject':
        database.claims.update_one({'_id': claim['_id']}, {'$set': {'status': 'rejected'}})
        flash('Claim rejected.', 'info')

    return redirect(url_for('dashboard'))


# ─────────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    database = get_db()
    if database is None:
        return render_template('admin.html', stats={}, users=[], items=[])

    q         = request.args.get('q', '').strip()
    item_type = request.args.get('type', '')
    status    = request.args.get('status', '')
    page      = max(1, int(request.args.get('page', 1)))

    query = {}
    if q:
        safe_q = re.escape(q)
        query['$or'] = [
            {'title'      : {'$regex': safe_q, '$options': 'i'}},
            {'description': {'$regex': safe_q, '$options': 'i'}},
        ]
    if item_type in ('lost', 'found'):
        query['type'] = item_type
    if status in ('active', 'claimed', 'returned'):
        query['status'] = status

    per_page = 15
    total    = database.items.count_documents(query)
    items    = list(database.items.find(query).sort('created_at', DESCENDING)
                    .skip((page - 1) * per_page).limit(per_page))
    pages    = max(1, (total + per_page - 1) // per_page)

    # Attach owner info
    for it in items:
        it['owner'] = database.users.find_one({'_id': it['created_by']})

    users = list(database.users.find({'role': 'student'}).sort('created_at', DESCENDING))

    stats = {
        'total_users'   : database.users.count_documents({'role': 'student'}),
        'total_items'   : database.items.count_documents({}),
        'total_lost'    : database.items.count_documents({'type': 'lost'}),
        'total_found'   : database.items.count_documents({'type': 'found'}),
        'active_items'  : database.items.count_documents({'status': 'active'}),
        'claimed_items' : database.items.count_documents({'status': 'claimed'}),
        'returned_items': database.items.count_documents({'status': 'returned'}),
        'total_claims'  : database.claims.count_documents({}),
    }

    return render_template('admin.html',
                           stats=stats, users=users, items=items,
                           total=total, pages=pages, page=page,
                           q=q, item_type=item_type, status=status)


@app.route('/admin/items/<item_id>/delete', methods=['POST'])
@admin_required
@db_required
def admin_delete_item(item_id):
    database = get_db()
    item     = database.items.find_one({'_id': oid(item_id)})
    if not item:
        abort(404)
    database.items.delete_one({'_id': item['_id']})
    database.claims.delete_many({'item_id': item['_id']})
    flash('Item deleted by admin.', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/users/<user_id>/delete', methods=['POST'])
@admin_required
@db_required
def admin_delete_user(user_id):
    database = get_db()
    user     = database.users.find_one({'_id': oid(user_id)})
    if not user or user.get('role') == 'admin':
        abort(404)
    database.users.delete_one({'_id': user['_id']})
    database.items.delete_many({'created_by': user['_id']})
    flash('User and their items deleted.', 'info')
    return redirect(url_for('admin_dashboard'))


# ─────────────────────────────────────────────
# API helpers (AJAX)
# ─────────────────────────────────────────────

@app.route('/api/stats')
def api_stats():
    database = get_db()
    if database is None:
        return jsonify({'error': 'db unavailable'}), 503
    return jsonify({
        'total'   : database.items.count_documents({}),
        'lost'    : database.items.count_documents({'type': 'lost'}),
        'found'   : database.items.count_documents({'type': 'found'}),
        'returned': database.items.count_documents({'status': 'returned'}),
    })


@app.route('/api/health')
def api_health():
    database = get_db()
    is_connected = (database is not None)
    is_cloud = MONGO_URI.startswith('mongodb+srv://')

    data = {
        'status': 'healthy' if is_connected else 'unhealthy',
        'database_type': 'MongoDB Atlas Cloud' if is_cloud else 'Local MongoDB',
        'database_name': DB_NAME,
        'connected': is_connected,
    }
    if not is_connected:
        data['error'] = db_error_message or 'Database connection failed'
    else:
        data['collections'] = {
            'users': database.users.count_documents({}),
            'items': database.items.count_documents({}),
            'claims': database.claims.count_documents({}),
        }
    return jsonify(data), (200 if is_connected else 503)


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port       = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, port=port)
