"""
seed_data.py – Inserts sample data into MongoDB for demonstration.
Run ONCE: python seed_data.py

WARNING: Running again will skip existing items (safe to re-run).
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from datetime import datetime, timedelta
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME   = os.environ.get('DB_NAME', 'findit_db')

client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

print(f"[Seed] Connecting to {DB_NAME}...")

# ── Demo users ──────────────────────────────────
demo_users = [
    {
        'name'         : 'Alice Student',
        'email'        : 'alice@college.edu',
        'password_hash': generate_password_hash('Password1'),
        'role'         : 'student',
        'created_at'   : datetime.utcnow() - timedelta(days=30),
    },
    {
        'name'         : 'Bob Student',
        'email'        : 'bob@college.edu',
        'password_hash': generate_password_hash('Password1'),
        'role'         : 'student',
        'created_at'   : datetime.utcnow() - timedelta(days=25),
    },
]

user_ids = []
for u in demo_users:
    existing = db.users.find_one({'email': u['email']})
    if not existing:
        result = db.users.insert_one(u)
        user_ids.append(result.inserted_id)
        print(f"  [+] User: {u['email']}")
    else:
        user_ids.append(existing['_id'])
        print(f"  [=] User already exists: {u['email']}")

alice_id = user_ids[0]
bob_id   = user_ids[1]

# ── Sample items ─────────────────────────────────
sample_items = [
    {
        'title'          : 'Black Leather Wallet',
        'description'    : 'Black leather bifold wallet. Contains some cash and student ID. Lost near the main building entrance.',
        'type'           : 'lost',
        'category'       : 'Wallets',
        'location'       : 'Main Building',
        'date_lost_found': datetime.utcnow() - timedelta(days=5),
        'image_url'      : 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=400',
        'status'         : 'active',
        'created_by'     : alice_id,
        'created_at'     : datetime.utcnow() - timedelta(days=5),
        'updated_at'     : datetime.utcnow() - timedelta(days=5),
    },
    {
        'title'          : 'Samsung Galaxy A54',
        'description'    : 'Found a black Samsung phone near the cafeteria entrance. Screen has a small crack on the corner. Home screen has a blue wallpaper.',
        'type'           : 'found',
        'category'       : 'Mobile Phones',
        'location'       : 'Cafeteria',
        'date_lost_found': datetime.utcnow() - timedelta(days=3),
        'image_url'      : 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400',
        'status'         : 'active',
        'created_by'     : bob_id,
        'created_at'     : datetime.utcnow() - timedelta(days=3),
        'updated_at'     : datetime.utcnow() - timedelta(days=3),
    },
    {
        'title'          : 'College ID Card – Riya Sharma',
        'description'    : 'Lost my college student ID card. Name: Riya Sharma, Branch: CSE, Year: 3rd. Please contact if found.',
        'type'           : 'lost',
        'category'       : 'Identity Cards',
        'location'       : 'Library',
        'date_lost_found': datetime.utcnow() - timedelta(days=7),
        'image_url'      : '',
        'status'         : 'active',
        'created_by'     : alice_id,
        'created_at'     : datetime.utcnow() - timedelta(days=7),
        'updated_at'     : datetime.utcnow() - timedelta(days=7),
    },
    {
        'title'          : 'Engineering Mathematics Textbook',
        'description'    : 'Found an Engineering Mathematics textbook by B.S. Grewal in the library reading room. Name written inside: "Karthik M".',
        'type'           : 'found',
        'category'       : 'Books and Notes',
        'location'       : 'Library',
        'date_lost_found': datetime.utcnow() - timedelta(days=2),
        'image_url'      : 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400',
        'status'         : 'active',
        'created_by'     : bob_id,
        'created_at'     : datetime.utcnow() - timedelta(days=2),
        'updated_at'     : datetime.utcnow() - timedelta(days=2),
    },
    {
        'title'          : 'Sony WF-1000XM4 Bluetooth Earbuds',
        'description'    : 'Lost my Sony noise-cancelling earbuds (black case with gold logo). Last seen in the lab block area. Very important – they are expensive!',
        'type'           : 'lost',
        'category'       : 'Electronics',
        'location'       : 'Lab Block',
        'date_lost_found': datetime.utcnow() - timedelta(days=1),
        'image_url'      : 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400',
        'status'         : 'active',
        'created_by'     : alice_id,
        'created_at'     : datetime.utcnow() - timedelta(days=1),
        'updated_at'     : datetime.utcnow() - timedelta(days=1),
    },
    {
        'title'          : 'Blue College Backpack',
        'description'    : 'Found a blue Wildcraft backpack near the sports complex. Contains some notebooks and a water bottle. Owner can claim by describing the contents.',
        'type'           : 'found',
        'category'       : 'Bags',
        'location'       : 'Sports Complex',
        'date_lost_found': datetime.utcnow() - timedelta(hours=12),
        'image_url'      : 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400',
        'status'         : 'active',
        'created_by'     : bob_id,
        'created_at'     : datetime.utcnow() - timedelta(hours=12),
        'updated_at'     : datetime.utcnow() - timedelta(hours=12),
    },
    {
        'title'          : 'Key Chain with 3 Keys',
        'description'    : 'Found a red key chain with 3 keys and a small Ganesha pendant near the hostel A entrance.',
        'type'           : 'found',
        'category'       : 'Keys',
        'location'       : 'Hostel A',
        'date_lost_found': datetime.utcnow() - timedelta(days=4),
        'image_url'      : '',
        'status'         : 'returned',
        'created_by'     : alice_id,
        'created_at'     : datetime.utcnow() - timedelta(days=4),
        'updated_at'     : datetime.utcnow() - timedelta(days=1),
    },
    {
        'title'          : 'HP Laptop Charger',
        'description'    : 'Lost my HP laptop charger (65W, blue tip) in the main building computer lab. It has my name written on the adapter with a marker.',
        'type'           : 'lost',
        'category'       : 'Electronics',
        'location'       : 'Main Building',
        'date_lost_found': datetime.utcnow() - timedelta(days=6),
        'image_url'      : '',
        'status'         : 'active',
        'created_by'     : bob_id,
        'created_at'     : datetime.utcnow() - timedelta(days=6),
        'updated_at'     : datetime.utcnow() - timedelta(days=6),
    },
]

inserted_count = 0
for item in sample_items:
    # Check if item with same title and created_by already exists
    existing = db.items.find_one({
        'title'     : item['title'],
        'created_by': item['created_by'],
    })
    if not existing:
        db.items.insert_one(item)
        inserted_count += 1
        print(f"  [+] Item: {item['title']} ({item['type']})")
    else:
        print(f"  [=] Item already exists: {item['title']}")

print(f"\n[Seed] Done! Inserted {inserted_count} new items.")
print("\n  Demo credentials:")
print("  Student 1: alice@college.edu / Password1")
print("  Student 2: bob@college.edu   / Password1")
print("\n  Admin: check ADMIN_EMAIL / ADMIN_PASSWORD in your .env file")
print("         (defaults: admin@findit.edu / Admin@1234)")
