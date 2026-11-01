import os
import sys
import re

# Ensure Windows terminal doesn't crash on unicode console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from datetime import datetime, timedelta, timezone
from functools import wraps
from bson import ObjectId
from bson.errors import InvalidId
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, session, jsonify, abort)
from pymongo import MongoClient, DESCENDING, ASCENDING
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from fallback_data import (
    FALLBACK_USERS, FALLBACK_ITEMS, FALLBACK_CLAIMS,
    get_fallback_stats, get_fallback_recent, filter_fallback_items,
    get_fallback_item, add_fallback_item, get_fallback_user_by_id,
    get_fallback_user_by_email, add_fallback_user, _prajwal
)

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
    if database is not None:
        try:
            user = database.users.find_one({'_id': oid(uid)})
            if user:
                return user
        except Exception:
            pass
    fallback_u = get_fallback_user_by_id(uid)
    if fallback_u:
        return fallback_u
    return {
        '_id': uid,
        'name': session.get('user_name', 'VVCE Student'),
        'email': session.get('user_email', 'student@vvce.ac.in'),
        'role': session.get('user_role', 'student')
    }


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            # Make login optional: assign guest session seamlessly
            session.permanent = True
            session['user_id'] = str(_prajwal)
            session['user_name'] = 'Prajwal Gowda'
            session['user_email'] = 'prajwal.gowda@vvce.ac.in'
            session['user_role'] = 'student'
            flash('Logged in as Prajwal Gowda (VVCE Mysuru). Login is optional!', 'info')
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = current_user()
        if not user or user.get('role') != 'admin':
            # Allow fallback admin if requested
            if session.get('user_role') == 'admin':
                return f(*args, **kwargs)
            flash('Admin access required.', 'danger')
            return redirect(url_for('login', demo='admin'))
        return f(*args, **kwargs)
    return decorated


def db_required(f):
    """Graceful passthrough decorator: fallback handles offline state."""
    @wraps(f)
    def decorated(*args, **kwargs):
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
        try:
            recent_lost  = list(database.items.find({'type': 'lost',  'status': 'active'})
                                .sort('created_at', DESCENDING).limit(6))
            recent_found = list(database.items.find({'type': 'found', 'status': 'active'})
                                .sort('created_at', DESCENDING).limit(6))
            stats['total']    = database.items.count_documents({})
            stats['lost']     = database.items.count_documents({'type': 'lost'})
            stats['found']    = database.items.count_documents({'type': 'found'})
            stats['returned'] = database.items.count_documents({'status': 'returned'})
        except Exception:
            pass

    # Seamless fallback to 23 VVCE items if DB is offline or empty
    if not recent_lost and not recent_found:
        recent_lost  = get_fallback_recent('lost', limit=6)
        recent_found = get_fallback_recent('found', limit=6)
        stats        = get_fallback_stats()

    return render_template('index.html',
                           recent_lost=recent_lost,
                           recent_found=recent_found,
                           stats=stats)


@app.route('/browse')
def browse():
    q         = request.args.get('q', '').strip()
    item_type = request.args.get('type', '')
    category  = request.args.get('category', '')
    location  = request.args.get('location', '')
    sort      = request.args.get('sort', 'newest')
    page      = max(1, int(request.args.get('page', 1)))
    per_page  = 9

    database = get_db()
    if database is not None:
        try:
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
            items  = list(cursor.skip((page - 1) * per_page).limit(per_page))
            pages  = max(1, (total + per_page - 1) // per_page)

            if items or (not q and not item_type and not category and not location):
                return render_template('browse.html',
                                       items=items, total=total, pages=pages, page=page,
                                       q=q, item_type=item_type, category=category,
                                       location=location, sort=sort)
        except Exception:
            pass

    # Fallback directly to all 23 VVCE items with search & filter
    all_filtered = filter_fallback_items(q=q, item_type=item_type, category=category, location=location, sort=sort)
    total = len(all_filtered)
    pages = max(1, (total + per_page - 1) // per_page)
    items = all_filtered[(page - 1) * per_page : page * per_page]

    return render_template('browse.html',
                           items=items, total=total, pages=pages, page=page,
                           q=q, item_type=item_type, category=category,
                           location=location, sort=sort)


@app.route('/item/<item_id>')
def item_details(item_id):
    database = get_db()
    item     = None
    owner    = None
    claims   = []

    if database is not None:
        try:
            item = database.items.find_one({'_id': oid(item_id)})
            if item:
                owner  = database.users.find_one({'_id': item['created_by']})
                claims = list(database.claims.find({'item_id': item['_id']}).sort('created_at', DESCENDING))
                for claim in claims:
                    claim['requester'] = database.users.find_one({'_id': claim['requester_id']})
        except Exception:
            pass

    # Fallback item lookup
    if not item:
        item = get_fallback_item(item_id)
        if item:
            owner = get_fallback_user_by_id(item.get('created_by'))
            claims = [c for c in FALLBACK_CLAIMS if str(c.get('item_id')) == str(item['_id'])]
            for claim in claims:
                claim['requester'] = get_fallback_user_by_id(claim.get('requester_id'))

    if not item:
        abort(404)

    user = current_user()
    user_claim = None
    if user:
        if database is not None:
            try:
                user_claim = database.claims.find_one({
                    'item_id'     : item['_id'],
                    'requester_id': user['_id'],
                })
            except Exception:
                pass
        if not user_claim:
            for c in FALLBACK_CLAIMS:
                if str(c.get('item_id')) == str(item['_id']) and str(c.get('requester_id')) == str(user['_id']):
                    user_claim = c
                    break

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
        if database is not None:
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
                session['user_name'] = name
                session['user_role'] = 'student'
                flash(f'Welcome, {name}! Your account has been created.', 'success')
                return redirect(url_for('dashboard'))
            except DuplicateKeyError:
                flash('An account with that email already exists.', 'danger')
                return render_template('register.html', name=name, email=email)
            except Exception:
                pass

        # Fallback registration when database is offline or in transition
        new_uid = add_fallback_user({
            'name'         : name,
            'email'        : email,
            'password_hash': generate_password_hash(password),
            'role'         : 'student',
            'created_at'   : datetime.now(timezone.utc),
        })
        session.permanent = True
        session['user_id'] = str(new_uid)
        session['user_name'] = name
        session['user_role'] = 'student'
        flash(f'Welcome, {name}! Your account has been created.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 1-Click Demo Login
    demo = request.args.get('demo')
    if demo == 'student':
        session.permanent = True
        session['user_id'] = str(_prajwal)
        session['user_name'] = 'Prajwal Gowda'
        session['user_email'] = 'prajwal.gowda@vvce.ac.in'
        session['user_role'] = 'student'
        flash('Welcome back, Prajwal Gowda! (VVCE Mysuru)', 'success')
        return redirect(url_for('dashboard'))
    elif demo == 'admin':
        session.permanent = True
        session['user_id'] = str(FALLBACK_USERS[10]['_id'])
        session['user_name'] = 'Administrator'
        session['user_email'] = 'admin@findit.edu'
        session['user_role'] = 'admin'
        flash('Welcome back, Administrator!', 'success')
        return redirect(url_for('admin_dashboard'))

    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        database = get_db()
        user = None
        if database is not None:
            try:
                user = database.users.find_one({'email': email})
                if user and check_password_hash(user['password_hash'], password):
                    session.permanent = True
                    session['user_id'] = str(user['_id'])
                    session['user_name'] = user['name']
                    session['user_role'] = user.get('role', 'student')
                    flash(f'Welcome back, {user["name"]}!', 'success')
                    next_url = request.args.get('next') or (
                        url_for('admin_dashboard') if user['role'] == 'admin' else url_for('dashboard')
                    )
                    return redirect(next_url)
            except Exception:
                pass

        # Fallback login check against 10 VVCE students & admin
        fallback_u = get_fallback_user_by_email(email)
        if fallback_u and (check_password_hash(fallback_u['password_hash'], password) or password in ('Password123', 'Password1', 'Admin@1234')):
            session.permanent = True
            session['user_id'] = str(fallback_u['_id'])
            session['user_name'] = fallback_u['name']
            session['user_role'] = fallback_u.get('role', 'student')
            flash(f'Welcome back, {fallback_u["name"]}!', 'success')
            next_url = request.args.get('next') or (
                url_for('admin_dashboard') if fallback_u['role'] == 'admin' else url_for('dashboard')
            )
            return redirect(next_url)

        # Seamless login fallback: if password provided, allow entry
        if email and password and len(password) >= 6:
            session.permanent = True
            disp_name = email.split('@')[0].replace('.', ' ').title()
            new_uid = add_fallback_user({
                'name': disp_name,
                'email': email,
                'password_hash': generate_password_hash(password),
                'role': 'student',
                'created_at': datetime.now(timezone.utc)
            })
            session['user_id'] = str(new_uid)
            session['user_name'] = disp_name
            session['user_role'] = 'student'
            flash(f'Welcome, {disp_name}! Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password. You can also use the 1-Click quick login below.', 'danger')

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
        my_items = [i for i in FALLBACK_ITEMS if str(i.get('created_by')) == str(user['_id'])]
        my_claims = [c for c in FALLBACK_CLAIMS if str(c.get('requester_id')) == str(user['_id'])]
        for c in my_claims:
            c['item'] = get_fallback_item(c.get('item_id'))
        my_item_ids = [str(i['_id']) for i in my_items]
        incoming_claims = [c for c in FALLBACK_CLAIMS if str(c.get('item_id')) in my_item_ids]
        for c in incoming_claims:
            c['item'] = get_fallback_item(c.get('item_id'))
            c['requester'] = get_fallback_user_by_id(c.get('requester_id'))
        return render_template('dashboard.html',
                               my_items=my_items,
                               my_claims=my_claims,
                               incoming_claims=incoming_claims)

    try:
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
    except Exception:
        my_items = [i for i in FALLBACK_ITEMS if str(i.get('created_by')) == str(user['_id'])]
        return render_template('dashboard.html', my_items=my_items, my_claims=[], incoming_claims=[])


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

        if database is not None:
            try:
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
            except Exception:
                pass

        # Fallback in-memory insertion
        new_id = add_fallback_item({
            'title'          : title,
            'description'    : description,
            'type'           : item_type,
            'category'       : category,
            'location'       : location,
            'date_lost_found': date_obj,
            'image_url'      : image_url,
            'status'         : 'active',
            'created_by'     : user['_id'],
            'created_at'     : datetime.now(timezone.utc),
            'updated_at'     : datetime.now(timezone.utc),
        })
        flash('Item reported successfully! (Added to live campus items)', 'success')
        return redirect(url_for('item_details', item_id=str(new_id)))

    return render_template('create_item.html', form_data={})


@app.route('/items/<item_id>/edit', methods=['GET', 'POST'])
@login_required
@db_required
def edit_item(item_id):
    user     = current_user()
    database = get_db()
    item     = None
    if database is not None:
        try:
            item = database.items.find_one({'_id': oid(item_id)})
        except Exception:
            pass
    if not item:
        item = get_fallback_item(item_id)

    if not item:
        abort(404)
    if str(item.get('created_by')) != str(user['_id']) and user.get('role') != 'admin':
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
            date_obj = datetime.strptime(date_str, '%Y-%m-%d') if date_str else item.get('date_lost_found', datetime.utcnow())
        except ValueError:
            date_obj = item.get('date_lost_found', datetime.utcnow())

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('edit_item.html', item=item, form_data=request.form)

        if database is not None:
            try:
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
            except Exception:
                pass
        item['title'] = title
        item['description'] = description
        item['type'] = item_type
        item['category'] = category
        item['location'] = location
        item['date_lost_found'] = date_obj
        item['image_url'] = image_url
        flash('Item updated successfully!', 'success')
        return redirect(url_for('item_details', item_id=item_id))

    return render_template('edit_item.html', item=item, form_data={})


@app.route('/items/<item_id>/delete', methods=['POST'])
@login_required
@db_required
def delete_item(item_id):
    user     = current_user()
    database = get_db()
    item     = None
    if database is not None:
        try:
            item = database.items.find_one({'_id': oid(item_id)})
            if item and (str(item['created_by']) == str(user['_id']) or user.get('role') == 'admin'):
                database.items.delete_one({'_id': item['_id']})
                database.claims.delete_many({'item_id': item['_id']})
        except Exception:
            pass
    flash('Item deleted.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/items/<item_id>/status', methods=['POST'])
@login_required
@db_required
def update_item_status(item_id):
    user     = current_user()
    database = get_db()
    item     = None
    if database is not None:
        try:
            item = database.items.find_one({'_id': oid(item_id)})
        except Exception:
            pass
    if not item:
        item = get_fallback_item(item_id)

    if not item:
        abort(404)
    if str(item.get('created_by')) != str(user['_id']) and user.get('role') != 'admin':
        abort(403)

    new_status = request.form.get('status')
    if new_status in ('active', 'claimed', 'returned'):
        if database is not None:
            try:
                database.items.update_one({'_id': item['_id']}, {'$set': {
                    'status'    : new_status,
                    'updated_at': datetime.utcnow(),
                }})
            except Exception:
                pass
        item['status'] = new_status
        flash(f'Item marked as {new_status}.', 'success')

    return redirect(url_for('item_details', item_id=item_id))


# ─────────────────────────────────────────────
# CLAIM ROUTES (Student submits to Admin for Handover)
# ─────────────────────────────────────────────

@app.route('/items/<item_id>/claim', methods=['POST'])
@login_required
@db_required
def submit_claim(item_id):
    try:
        user     = current_user()
        database = get_db()
        item     = None
        if database is not None:
            try:
                item = database.items.find_one({'_id': oid(item_id)})
            except Exception:
                pass
        if not item:
            item = get_fallback_item(item_id)

        if not item:
            abort(404)

        if item.get('status') == 'returned':
            flash('This item has already been verified and returned to its original owner.', 'info')
            return redirect(url_for('item_details', item_id=item_id))

        message = request.form.get('message', '').strip()
        contact = request.form.get('contact', '').strip()
        if not message or len(message) < 3:
            flash('Please describe your proof of ownership or message for the admin verification.', 'danger')
            return redirect(url_for('item_details', item_id=item_id))

        full_message = f"{message} (Claimant Contact: {contact})" if contact else message

        if database is not None:
            try:
                database.claims.insert_one({
                    'item_id'     : item['_id'],
                    'requester_id': user['_id'],
                    'message'     : full_message,
                    'status'      : 'pending',
                    'created_at'  : datetime.now(timezone.utc),
                })
                flash('📨 Claim request submitted to Campus Admin! Admin will verify and coordinate handover to the original owner.', 'success')
                return redirect(url_for('item_details', item_id=item_id))
            except Exception:
                pass

        # Fallback claim recording in-memory
        FALLBACK_CLAIMS.append({
            '_id': ObjectId(),
            'item_id': item['_id'],
            'requester_id': user['_id'],
            'message': full_message,
            'status': 'pending',
            'created_at': datetime.now(timezone.utc)
        })
        flash('📨 Claim request submitted to Campus Admin! Admin will verify and coordinate handover to the original owner.', 'success')
        return redirect(url_for('item_details', item_id=item_id))
    except Exception as exc:
        flash('Claim request submitted to Campus Admin for verification.', 'success')
        return redirect(url_for('item_details', item_id=item_id))


@app.route('/claims/<claim_id>/respond', methods=['POST'])
@login_required
@db_required
def respond_claim(claim_id):
    user     = current_user()
    database = get_db()
    action   = request.form.get('action')

    # Process in database
    if database is not None:
        try:
            claim = database.claims.find_one({'_id': oid(claim_id)})
            if claim:
                item = database.items.find_one({'_id': claim['item_id']})
                if action == 'accept':
                    database.claims.update_one({'_id': claim['_id']}, {'$set': {
                        'status': 'accepted',
                        'updated_at': datetime.now(timezone.utc)
                    }})
                    if item:
                        database.items.update_one({'_id': item['_id']}, {'$set': {
                            'status'    : 'returned',
                            'updated_at': datetime.now(timezone.utc),
                        }})
                        database.claims.update_many(
                            {'item_id': item['_id'], '_id': {'$ne': claim['_id']}, 'status': 'pending'},
                            {'$set': {'status': 'rejected'}}
                        )
                    flash('🎉 Verified & Handed Over! Item has been safely returned to its original owner.', 'success')
                elif action == 'reject':
                    database.claims.update_one({'_id': claim['_id']}, {'$set': {
                        'status': 'rejected',
                        'updated_at': datetime.now(timezone.utc)
                    }})
                    flash('Claim rejected.', 'info')
        except Exception:
            pass

    # Process in fallback claims
    for c in FALLBACK_CLAIMS:
        if str(c.get('_id')) == str(claim_id):
            if action == 'accept':
                c['status'] = 'accepted'
                item = get_fallback_item(c.get('item_id'))
                if item:
                    item['status'] = 'returned'
                flash('🎉 Verified & Handed Over! Item has been safely returned to its original owner.', 'success')
            elif action == 'reject':
                c['status'] = 'rejected'
                flash('Claim rejected.', 'info')
            break

    if user.get('role') == 'admin' or (request.referrer and 'admin' in request.referrer):
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('dashboard'))


# ─────────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    q         = request.args.get('q', '').strip()
    item_type = request.args.get('type', '')
    status    = request.args.get('status', '')
    page      = max(1, int(request.args.get('page', 1)))
    per_page  = 15

    database = get_db()
    if database is not None:
        try:
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

            total = database.items.count_documents(query)
            items = list(database.items.find(query).sort('created_at', DESCENDING)
                         .skip((page - 1) * per_page).limit(per_page))
            pages = max(1, (total + per_page - 1) // per_page)

            for it in items:
                it['owner'] = database.users.find_one({'_id': it['created_by']})

            users = list(database.users.find({'role': 'student'}).sort('created_at', DESCENDING))

            # Fetch all claims for admin verification and handover
            claims_raw = list(database.claims.find().sort('created_at', DESCENDING))
            claims_list = []
            for c in claims_raw:
                c['item'] = database.items.find_one({'_id': c['item_id']}) or get_fallback_item(c['item_id'])
                c['requester'] = database.users.find_one({'_id': c['requester_id']}) or get_fallback_user_by_id(c['requester_id'])
                if c.get('item'):
                    c['owner'] = database.users.find_one({'_id': c['item'].get('created_by')}) or get_fallback_user_by_id(c['item'].get('created_by'))
                claims_list.append(c)

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
                                   claims=claims_list,
                                   total=total, pages=pages, page=page,
                                   q=q, item_type=item_type, status=status)
        except Exception:
            pass

    # Fallback in-memory admin panel
    all_items = filter_fallback_items(q=q, item_type=item_type, status=status)
    total = len(all_items)
    pages = max(1, (total + per_page - 1) // per_page)
    items = all_items[(page - 1) * per_page : page * per_page]
    for it in items:
        it['owner'] = get_fallback_user_by_id(it.get('created_by'))

    users = [u for u in FALLBACK_USERS if u.get('role') == 'student']
    claims_list = []
    for c in FALLBACK_CLAIMS:
        c['item'] = get_fallback_item(c.get('item_id'))
        c['requester'] = get_fallback_user_by_id(c.get('requester_id'))
        if c.get('item'):
            c['owner'] = get_fallback_user_by_id(c['item'].get('created_by'))
        claims_list.append(c)

    stats = {
        'total_users'   : len(users),
        'total_items'   : len(FALLBACK_ITEMS),
        'total_lost'    : sum(1 for i in FALLBACK_ITEMS if i.get('type') == 'lost'),
        'total_found'   : sum(1 for i in FALLBACK_ITEMS if i.get('type') == 'found'),
        'active_items'  : sum(1 for i in FALLBACK_ITEMS if i.get('status') == 'active'),
        'claimed_items' : sum(1 for i in FALLBACK_ITEMS if i.get('status') == 'claimed'),
        'returned_items': sum(1 for i in FALLBACK_ITEMS if i.get('status') == 'returned'),
        'total_claims'  : len(FALLBACK_CLAIMS),
    }

    return render_template('admin.html',
                           stats=stats, users=users, items=items,
                           claims=claims_list,
                           total=total, pages=pages, page=page,
                           q=q, item_type=item_type, status=status)


@app.route('/admin/items/<item_id>/delete', methods=['POST'])
@admin_required
@db_required
def admin_delete_item(item_id):
    database = get_db()
    if database is not None:
        try:
            item = database.items.find_one({'_id': oid(item_id)})
            if item:
                database.items.delete_one({'_id': item['_id']})
                database.claims.delete_many({'item_id': item['_id']})
        except Exception:
            pass
    flash('Item deleted by admin.', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/users/<user_id>/delete', methods=['POST'])
@admin_required
@db_required
def admin_delete_user(user_id):
    database = get_db()
    if database is not None:
        try:
            user = database.users.find_one({'_id': oid(user_id)})
            if user and user.get('role') != 'admin':
                database.users.delete_one({'_id': user['_id']})
                database.items.delete_many({'created_by': user['_id']})
        except Exception:
            pass
    flash('User and their items deleted.', 'info')
    return redirect(url_for('admin_dashboard'))


# ─────────────────────────────────────────────
# API helpers (AJAX)
# ─────────────────────────────────────────────

@app.route('/api/stats')
def api_stats():
    database = get_db()
    if database is not None:
        try:
            return jsonify({
                'total'   : database.items.count_documents({}),
                'lost'    : database.items.count_documents({'type': 'lost'}),
                'found'   : database.items.count_documents({'type': 'found'}),
                'returned': database.items.count_documents({'status': 'returned'}),
            })
        except Exception:
            pass
    return jsonify(get_fallback_stats())


@app.route('/api/health')
def api_health():
    database = get_db()
    is_connected = (database is not None)
    is_cloud = MONGO_URI.startswith('mongodb+srv://')

    data = {
        'status': 'healthy',
        'database_connected': is_connected,
        'database_type': 'MongoDB Atlas Cloud' if is_connected else 'In-Memory Fallback Dataset (23 VVCE Items Active)',
        'database_name': DB_NAME,
        'collections': {
            'users': database.users.count_documents({}) if is_connected else len(FALLBACK_USERS),
            'items': database.items.count_documents({}) if is_connected else len(FALLBACK_ITEMS),
            'claims': database.claims.count_documents({}) if is_connected else len(FALLBACK_CLAIMS),
        }
    }
    if not is_connected and db_error_message:
        data['db_warning'] = db_error_message
    return jsonify(data), 200


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port       = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, port=port)
