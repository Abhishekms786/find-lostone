"""
seed_vvce_data.py - Seeds 23 realistic Karnataka lost & found items and students
from Vidyavardhaka College of Engineering (VVCE), Mysuru into MongoDB Atlas.
"""
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = os.environ.get('DB_NAME', 'findit_db')

if not MONGO_URI:
    print("[ERROR] MONGO_URI not found in .env")
    sys.exit(1)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
now = datetime.now(timezone.utc)

print(f"[VVCE Seed] Connecting to {db.name}...")

# ── 1. Create Karnataka Students (VVCE Mysuru) ──
karnataka_students = [
    {'name': 'Prajwal Gowda',     'email': 'prajwal.gowda@vvce.ac.in',     'password_hash': generate_password_hash('Password123'), 'role': 'student', 'created_at': now - timedelta(days=60)},
    {'name': 'Ananya Bhat',       'email': 'ananya.bhat@vvce.ac.in',       'password_hash': generate_password_hash('Password123'), 'role': 'student', 'created_at': now - timedelta(days=55)},
    {'name': 'Darshan Kumar M',   'email': 'darshan.km@vvce.ac.in',        'password_hash': generate_password_hash('Password123'), 'role': 'student', 'created_at': now - timedelta(days=50)},
    {'name': 'Spandana Hegde',    'email': 'spandana.hegde@vvce.ac.in',    'password_hash': generate_password_hash('Password123'), 'role': 'student', 'created_at': now - timedelta(days=45)},
    {'name': 'Chethan Gowda K',   'email': 'chethan.gk@vvce.ac.in',        'password_hash': generate_password_hash('Password123'), 'role': 'student', 'created_at': now - timedelta(days=40)},
    {'name': 'Varsha Kulkarni',   'email': 'varsha.k@vvce.ac.in',          'password_hash': generate_password_hash('Password123'), 'role': 'student', 'created_at': now - timedelta(days=35)},
    {'name': 'Rohith Shenoy',     'email': 'rohith.shenoy@vvce.ac.in',     'password_hash': generate_password_hash('Password123'), 'role': 'student', 'created_at': now - timedelta(days=30)},
    {'name': 'Sinchana Rao',      'email': 'sinchana.rao@vvce.ac.in',      'password_hash': generate_password_hash('Password123'), 'role': 'student', 'created_at': now - timedelta(days=25)},
    {'name': 'Likith N',          'email': 'likith.n@vvce.ac.in',          'password_hash': generate_password_hash('Password123'), 'role': 'student', 'created_at': now - timedelta(days=20)},
    {'name': 'Tejaswini Murthy',  'email': 'tejaswini.m@vvce.ac.in',       'password_hash': generate_password_hash('Password123'), 'role': 'student', 'created_at': now - timedelta(days=15)},
]

student_ids = []
for s in karnataka_students:
    existing = db.users.find_one({'email': s['email']})
    if not existing:
        res = db.users.insert_one(s)
        student_ids.append(res.inserted_id)
        print(f"  [+] Student created: {s['name']} ({s['email']})")
    else:
        student_ids.append(existing['_id'])
        print(f"  [=] Student exists: {s['name']}")

prajwal, ananya, darshan, spandana, chethan, varsha, rohith, sinchana, likith, tejaswini = student_ids[:10]

# ── 2. 23 Realistic Campus Items (VVCE Mysuru Context) ──
vvce_items = [
    {
        'title': 'Casio fx-991CW ClassWiz Calculator',
        'description': 'Lost my scientific calculator during 3rd sem VTU Internal Assessment in CS Block room 204. Name "Prajwal" written on the back cover with a black marker.',
        'type': 'lost',
        'category': 'Electronics',
        'location': 'Lab Block',
        'date_lost_found': now - timedelta(days=1),
        'image_url': 'https://images.unsplash.com/photo-1594980596870-8aa52a78d8cd?w=500',
        'status': 'active',
        'created_by': prajwal,
        'created_at': now - timedelta(days=1),
        'updated_at': now - timedelta(days=1)
    },
    {
        'title': 'Honda Activa Key with Mysore Palace Keychain',
        'description': 'Found a single Honda Activa 6G key with a brass Mysore Palace keychain near Gate 2 two-wheeler parking lot. Handed over to security guard or claim here.',
        'type': 'found',
        'category': 'Keys',
        'location': 'Parking Area',
        'date_lost_found': now - timedelta(hours=8),
        'image_url': 'https://images.unsplash.com/photo-1582139329536-e7284fece509?w=500',
        'status': 'active',
        'created_by': darshan,
        'created_at': now - timedelta(hours=8),
        'updated_at': now - timedelta(hours=8)
    },
    {
        'title': 'VTU College ID Card & Bus Pass – Ananya Bhat',
        'description': 'Lost blue VVCE Student ID card along with KSRTC Mysuru City Bus Pass (Route: Kuvempunagar to VVCE Gokulam). Kept inside a transparent pouch.',
        'type': 'lost',
        'category': 'Identity Cards',
        'location': 'Cafeteria',
        'date_lost_found': now - timedelta(days=2),
        'image_url': '',
        'status': 'active',
        'created_by': ananya,
        'created_at': now - timedelta(days=2),
        'updated_at': now - timedelta(days=2)
    },
    {
        'title': 'Boat Airdopes 141 (White Charging Case)',
        'description': 'Found a pair of Boat Bluetooth earbuds in a white case on desk #14 in Library 1st floor reference section. Left during the 11 AM study break.',
        'type': 'found',
        'category': 'Electronics',
        'location': 'Library',
        'date_lost_found': now - timedelta(hours=14),
        'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500',
        'status': 'active',
        'created_by': chethan,
        'created_at': now - timedelta(hours=14),
        'updated_at': now - timedelta(hours=14)
    },
    {
        'title': 'Brown Wildcraft Leather Bi-Fold Wallet',
        'description': 'Lost brown wallet near campus canteen during lunch. Contains driving license, SBI ATM card (blocked), and some cash. Please return the cards urgently.',
        'type': 'lost',
        'category': 'Wallets',
        'location': 'Cafeteria',
        'date_lost_found': now - timedelta(days=3),
        'image_url': 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=500',
        'status': 'active',
        'created_by': rohith,
        'created_at': now - timedelta(days=3),
        'updated_at': now - timedelta(days=3)
    },
    {
        'title': 'Engineering Mathematics-III Textbook (B.S. Grewal)',
        'description': 'Found Higher Engineering Mathematics book left on the concrete benches near Tapasya Amphitheatre. Has VVCE library stamp on the first page.',
        'type': 'found',
        'category': 'Books and Notes',
        'location': 'Main Building',
        'date_lost_found': now - timedelta(days=2),
        'image_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500',
        'status': 'active',
        'created_by': spandana,
        'created_at': now - timedelta(days=2),
        'updated_at': now - timedelta(days=2)
    },
    {
        'title': 'Fastrack Navy Blue Laptop Backpack',
        'description': 'Lost navy blue Fastrack backpack in Mechanical Block CAD Lab. Contains 1 subject notebook and a yellow water bottle. No laptop inside.',
        'type': 'lost',
        'category': 'Bags',
        'location': 'Lab Block',
        'date_lost_found': now - timedelta(days=4),
        'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500',
        'status': 'active',
        'created_by': chethan,
        'created_at': now - timedelta(days=4),
        'updated_at': now - timedelta(days=4)
    },
    {
        'title': 'Realme 65W SuperDart Fast Charger with Yellow Cable',
        'description': 'Found a white Realme adapter with signature yellow Type-C cable plugged into the power socket in Room 312, Sir MV Block.',
        'type': 'found',
        'category': 'Electronics',
        'location': 'Main Building',
        'date_lost_found': now - timedelta(days=1),
        'image_url': '',
        'status': 'active',
        'created_by': sinchana,
        'created_at': now - timedelta(days=1),
        'updated_at': now - timedelta(days=1)
    },
    {
        'title': 'Noise ColorFit Pulse Smartwatch (Black Strap)',
        'description': 'Lost my smartwatch on the outdoor basketball court during the evening match. Screen protector has minor air bubble on top-right edge.',
        'type': 'lost',
        'category': 'Accessories',
        'location': 'Sports Complex',
        'date_lost_found': now - timedelta(days=2),
        'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
        'status': 'active',
        'created_by': likith,
        'created_at': now - timedelta(days=2),
        'updated_at': now - timedelta(days=2)
    },
    {
        'title': 'Spectacles with Matte Black Frame (Lenskart Air)',
        'description': 'Found reading glasses in a hard blue case left on the counter of Gokulam Campus Canteen juice shop.',
        'type': 'found',
        'category': 'Accessories',
        'location': 'Cafeteria',
        'date_lost_found': now - timedelta(hours=18),
        'image_url': 'https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=500',
        'status': 'active',
        'created_by': varsha,
        'created_at': now - timedelta(hours=18),
        'updated_at': now - timedelta(hours=18)
    },
    {
        'title': 'Data Structures Lab Record (Handwritten with Diagrams)',
        'description': 'Lost blue hardbound DS Record Notebook before lab external submission. Last seen near EC Dept HOD office corridor. Very urgent!',
        'type': 'lost',
        'category': 'Books and Notes',
        'location': 'Lab Block',
        'date_lost_found': now - timedelta(days=1),
        'image_url': '',
        'status': 'active',
        'created_by': tejaswini,
        'created_at': now - timedelta(days=1),
        'updated_at': now - timedelta(days=1)
    },
    {
        'title': 'Yamaha FZ-S Bike Key with Royal Enfield Fabric Tag',
        'description': 'Found single bike key near VVCE Main Gate entry ramp. Red Royal Enfield "Made Like a Gun" fabric tag attached.',
        'type': 'found',
        'category': 'Keys',
        'location': 'Parking Area',
        'date_lost_found': now - timedelta(days=3),
        'image_url': '',
        'status': 'active',
        'created_by': prajwal,
        'created_at': now - timedelta(days=3),
        'updated_at': now - timedelta(days=3)
    },
    {
        'title': 'OnePlus Nord CE 3 (Aqua Surge Color)',
        'description': 'Lost my OnePlus phone with transparent case and sticker of Royal Challengers Bangalore (RCB). Lost near Auditorium stage.',
        'type': 'lost',
        'category': 'Mobile Phones',
        'location': 'Auditorium',
        'date_lost_found': now - timedelta(days=5),
        'image_url': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500',
        'status': 'active',
        'created_by': darshan,
        'created_at': now - timedelta(days=5),
        'updated_at': now - timedelta(days=5)
    },
    {
        'title': 'Milton Thermosteel 1000ml Bottle (Matte Blue)',
        'description': 'Found blue insulated Milton water bottle in Badminton Court viewing gallery after college sports practice.',
        'type': 'found',
        'category': 'Other',
        'location': 'Sports Complex',
        'date_lost_found': now - timedelta(days=2),
        'image_url': '',
        'status': 'active',
        'created_by': spandana,
        'created_at': now - timedelta(days=2),
        'updated_at': now - timedelta(days=2)
    },
    {
        'title': 'SanDisk Ultra Dual 64GB Pendrive (Type-C & Type-A)',
        'description': 'Silver metallic USB drive lost in Seminar Hall 2 during 8th semester Major Project PPT review. Contains project source code.',
        'type': 'lost',
        'category': 'Electronics',
        'location': 'Auditorium',
        'date_lost_found': now - timedelta(days=3),
        'image_url': '',
        'status': 'active',
        'created_by': rohith,
        'created_at': now - timedelta(days=3),
        'updated_at': now - timedelta(days=3)
    },
    {
        'title': 'Yonex Nanoray 70 Light Badminton Racket',
        'description': 'Found Yonex racket in full black cover inside Indoor Gymnasium locker area. Left behind on Saturday morning.',
        'type': 'found',
        'category': 'Other',
        'location': 'Sports Complex',
        'date_lost_found': now - timedelta(days=4),
        'image_url': '',
        'status': 'claimed',
        'created_by': chethan,
        'created_at': now - timedelta(days=4),
        'updated_at': now - timedelta(days=1)
    },
    {
        'title': 'Redmi Note 12 5G (Frosted Green)',
        'description': 'Found a green Redmi phone on bench near Sir MV statue. Locked with pattern. Battery was at 45% when found.',
        'type': 'found',
        'category': 'Mobile Phones',
        'location': 'Main Building',
        'date_lost_found': now - timedelta(hours=6),
        'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500',
        'status': 'active',
        'created_by': sinchana,
        'created_at': now - timedelta(hours=6),
        'updated_at': now - timedelta(hours=6)
    },
    {
        'title': 'Titan Karishma Analog Watch (Golden Dial)',
        'description': 'Lost classic Titan watch with brown leather strap in Admin Block fee counter queue. Family gift with sentimental value.',
        'type': 'lost',
        'category': 'Accessories',
        'location': 'Admin Block',
        'date_lost_found': now - timedelta(days=6),
        'image_url': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=500',
        'status': 'active',
        'created_by': varsha,
        'created_at': now - timedelta(days=6),
        'updated_at': now - timedelta(days=6)
    },
    {
        'title': 'Mechanical Engineering Mini Drafter with Canvas Cover',
        'description': 'Found Omega brand mini drafter in Chennaiah Mechanical Workshop drawing hall. Initials "K.M." etched on ruler.',
        'type': 'found',
        'category': 'Other',
        'location': 'Lab Block',
        'date_lost_found': now - timedelta(days=3),
        'image_url': '',
        'status': 'returned',
        'created_by': likith,
        'created_at': now - timedelta(days=3),
        'updated_at': now - timedelta(hours=4)
    },
    {
        'title': 'Black Nike Dri-FIT Sports Zipper Jacket',
        'description': 'Left black Nike hoodie jacket on bleachers of college football ground after inter-branch tournament match.',
        'type': 'lost',
        'category': 'Clothing',
        'location': 'Sports Complex',
        'date_lost_found': now - timedelta(days=5),
        'image_url': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=500',
        'status': 'active',
        'created_by': prajwal,
        'created_at': now - timedelta(days=5),
        'updated_at': now - timedelta(days=5)
    },
    {
        'title': 'Ladies Leather Handbag (Maroon Color)',
        'description': 'Found maroon handbag on sofa in Placement Cell waiting lobby. Contains cosmetics, notebook, and college syllabus copy.',
        'type': 'found',
        'category': 'Bags',
        'location': 'Admin Block',
        'date_lost_found': now - timedelta(days=2),
        'image_url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=500',
        'status': 'active',
        'created_by': tejaswini,
        'created_at': now - timedelta(days=2),
        'updated_at': now - timedelta(days=2)
    },
    {
        'title': 'Apple AirPods Pro (2nd Gen) in MagSafe Case',
        'description': 'Lost AirPods Pro near Gokulam 3rd stage auto stand just outside VVCE college campus gate. Case has a spigen black bumper sleeve.',
        'type': 'lost',
        'category': 'Electronics',
        'location': 'Other',
        'date_lost_found': now - timedelta(days=1),
        'image_url': 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500',
        'status': 'active',
        'created_by': ananya,
        'created_at': now - timedelta(days=1),
        'updated_at': now - timedelta(days=1)
    },
    {
        'title': 'Tupperware Lunch Bag with 3 Steel Dabbas',
        'description': 'Found red insulated lunch tote bag on stone bench near civil dept water cooler. Handed to security office.',
        'type': 'found',
        'category': 'Other',
        'location': 'Main Building',
        'date_lost_found': now - timedelta(hours=10),
        'image_url': '',
        'status': 'returned',
        'created_by': darshan,
        'created_at': now - timedelta(hours=10),
        'updated_at': now - timedelta(hours=2)
    }
]

inserted_items = 0
for item in vvce_items:
    existing = db.items.find_one({
        'title': item['title'],
        'created_by': item['created_by']
    })
    if not existing:
        db.items.insert_one(item)
        inserted_items += 1
        print(f"  [+] Item: {item['title']} ({item['type']})")
    else:
        print(f"  [=] Item exists: {item['title']}")

print(f"\n[VVCE Seed Complete] Successfully inserted {inserted_items} items into MongoDB Atlas findit_db!")
