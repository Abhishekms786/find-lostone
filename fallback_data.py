"""
In-memory and fallback dataset for FindIt.
Contains 23 realistic Karnataka items and 10 students from VVCE Mysuru.
Ensures the app functions seamlessly and immediately even if MongoDB Atlas
network access is in transition or unavailable.
"""

from datetime import datetime, timedelta, timezone
from bson import ObjectId
from werkzeug.security import generate_password_hash

now = datetime.now(timezone.utc)

# ── 10 Karnataka Students (VVCE Mysuru) ──
FALLBACK_USERS = [
    {
        '_id': ObjectId('6724ec010000000000000001'),
        'name': 'Prajwal Gowda',
        'email': 'prajwal.gowda@vvce.ac.in',
        'password_hash': generate_password_hash('Password123'),
        'role': 'student',
        'created_at': now - timedelta(days=60)
    },
    {
        '_id': ObjectId('6724ec010000000000000002'),
        'name': 'Ananya Bhat',
        'email': 'ananya.bhat@vvce.ac.in',
        'password_hash': generate_password_hash('Password123'),
        'role': 'student',
        'created_at': now - timedelta(days=55)
    },
    {
        '_id': ObjectId('6724ec010000000000000003'),
        'name': 'Darshan Kumar M',
        'email': 'darshan.km@vvce.ac.in',
        'password_hash': generate_password_hash('Password123'),
        'role': 'student',
        'created_at': now - timedelta(days=50)
    },
    {
        '_id': ObjectId('6724ec010000000000000004'),
        'name': 'Spandana Hegde',
        'email': 'spandana.hegde@vvce.ac.in',
        'password_hash': generate_password_hash('Password123'),
        'role': 'student',
        'created_at': now - timedelta(days=45)
    },
    {
        '_id': ObjectId('6724ec010000000000000005'),
        'name': 'Chethan Gowda K',
        'email': 'chethan.gk@vvce.ac.in',
        'password_hash': generate_password_hash('Password123'),
        'role': 'student',
        'created_at': now - timedelta(days=40)
    },
    {
        '_id': ObjectId('6724ec010000000000000006'),
        'name': 'Varsha Kulkarni',
        'email': 'varsha.k@vvce.ac.in',
        'password_hash': generate_password_hash('Password123'),
        'role': 'student',
        'created_at': now - timedelta(days=35)
    },
    {
        '_id': ObjectId('6724ec010000000000000007'),
        'name': 'Rohith Shenoy',
        'email': 'rohith.shenoy@vvce.ac.in',
        'password_hash': generate_password_hash('Password123'),
        'role': 'student',
        'created_at': now - timedelta(days=30)
    },
    {
        '_id': ObjectId('6724ec010000000000000008'),
        'name': 'Sinchana Rao',
        'email': 'sinchana.rao@vvce.ac.in',
        'password_hash': generate_password_hash('Password123'),
        'role': 'student',
        'created_at': now - timedelta(days=25)
    },
    {
        '_id': ObjectId('6724ec010000000000000009'),
        'name': 'Likith N',
        'email': 'likith.n@vvce.ac.in',
        'password_hash': generate_password_hash('Password123'),
        'role': 'student',
        'created_at': now - timedelta(days=20)
    },
    {
        '_id': ObjectId('6724ec01000000000000000a'),
        'name': 'Tejaswini Murthy',
        'email': 'tejaswini.m@vvce.ac.in',
        'password_hash': generate_password_hash('Password123'),
        'role': 'student',
        'created_at': now - timedelta(days=15)
    },
    {
        '_id': ObjectId('6724ec010000000000000000'),
        'name': 'Administrator',
        'email': 'admin@findit.edu',
        'password_hash': generate_password_hash('Admin@1234'),
        'role': 'admin',
        'created_at': now - timedelta(days=90)
    }
]

# ── 23 Realistic Campus Items (VVCE Mysuru Context) ──
_prajwal   = FALLBACK_USERS[0]['_id']
_ananya    = FALLBACK_USERS[1]['_id']
_darshan   = FALLBACK_USERS[2]['_id']
_spandana  = FALLBACK_USERS[3]['_id']
_chethan   = FALLBACK_USERS[4]['_id']
_varsha    = FALLBACK_USERS[5]['_id']
_rohith    = FALLBACK_USERS[6]['_id']
_sinchana  = FALLBACK_USERS[7]['_id']
_likith    = FALLBACK_USERS[8]['_id']
_tejaswini = FALLBACK_USERS[9]['_id']

FALLBACK_ITEMS = [
    {
        '_id': ObjectId('6724ed010000000000000001'),
        'title': 'Casio fx-991CW ClassWiz Calculator',
        'description': 'Lost my scientific calculator during 3rd sem VTU Internal Assessment in CS Block room 204. Name "Prajwal" written on the back cover with a black marker.',
        'type': 'lost',
        'category': 'Electronics',
        'location': 'Lab Block',
        'date_lost_found': now - timedelta(days=1),
        'image_url': 'https://images.unsplash.com/photo-1594980596870-8aa52a78d8cd?w=500',
        'status': 'active',
        'created_by': _prajwal,
        'created_at': now - timedelta(days=1),
        'updated_at': now - timedelta(days=1)
    },
    {
        '_id': ObjectId('6724ed010000000000000002'),
        'title': 'Honda Activa Key with Mysore Palace Keychain',
        'description': 'Found a single Honda Activa 6G key with a brass Mysore Palace keychain near Gate 2 two-wheeler parking lot. Handed over to security guard or claim here.',
        'type': 'found',
        'category': 'Keys',
        'location': 'Parking Area',
        'date_lost_found': now - timedelta(hours=8),
        'image_url': 'https://images.unsplash.com/photo-1582139329536-e7284fece509?w=500',
        'status': 'active',
        'created_by': _darshan,
        'created_at': now - timedelta(hours=8),
        'updated_at': now - timedelta(hours=8)
    },
    {
        '_id': ObjectId('6724ed010000000000000003'),
        'title': 'VTU College ID Card & Bus Pass – Ananya Bhat',
        'description': 'Lost blue VVCE Student ID card along with KSRTC Mysuru City Bus Pass (Route: Kuvempunagar to VVCE Gokulam). Kept inside a transparent pouch.',
        'type': 'lost',
        'category': 'Identity Cards',
        'location': 'Cafeteria',
        'date_lost_found': now - timedelta(days=2),
        'image_url': '',
        'status': 'active',
        'created_by': _ananya,
        'created_at': now - timedelta(days=2),
        'updated_at': now - timedelta(days=2)
    },
    {
        '_id': ObjectId('6724ed010000000000000004'),
        'title': 'Boat Airdopes 141 (White Charging Case)',
        'description': 'Found a pair of Boat Bluetooth earbuds in a white case on desk #14 in Library 1st floor reference section. Left during the 11 AM study break.',
        'type': 'found',
        'category': 'Electronics',
        'location': 'Library',
        'date_lost_found': now - timedelta(hours=14),
        'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500',
        'status': 'active',
        'created_by': _chethan,
        'created_at': now - timedelta(hours=14),
        'updated_at': now - timedelta(hours=14)
    },
    {
        '_id': ObjectId('6724ed010000000000000005'),
        'title': 'Brown Wildcraft Leather Bi-Fold Wallet',
        'description': 'Lost brown wallet near campus canteen during lunch. Contains driving license, SBI ATM card (blocked), and some cash. Please return the cards urgently.',
        'type': 'lost',
        'category': 'Wallets',
        'location': 'Cafeteria',
        'date_lost_found': now - timedelta(days=3),
        'image_url': 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=500',
        'status': 'active',
        'created_by': _rohith,
        'created_at': now - timedelta(days=3),
        'updated_at': now - timedelta(days=3)
    },
    {
        '_id': ObjectId('6724ed010000000000000006'),
        'title': 'Engineering Mathematics-III Textbook (B.S. Grewal)',
        'description': 'Found Higher Engineering Mathematics book left on the concrete benches near Tapasya Amphitheatre. Has VVCE library stamp on the first page.',
        'type': 'found',
        'category': 'Books and Notes',
        'location': 'Main Building',
        'date_lost_found': now - timedelta(days=2),
        'image_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500',
        'status': 'active',
        'created_by': _spandana,
        'created_at': now - timedelta(days=2),
        'updated_at': now - timedelta(days=2)
    },
    {
        '_id': ObjectId('6724ed010000000000000007'),
        'title': 'Fastrack Navy Blue Laptop Backpack',
        'description': 'Lost navy blue Fastrack backpack in Mechanical Block CAD Lab. Contains 1 subject notebook and a yellow water bottle. No laptop inside.',
        'type': 'lost',
        'category': 'Bags',
        'location': 'Lab Block',
        'date_lost_found': now - timedelta(days=4),
        'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500',
        'status': 'active',
        'created_by': _chethan,
        'created_at': now - timedelta(days=4),
        'updated_at': now - timedelta(days=4)
    },
    {
        '_id': ObjectId('6724ed010000000000000008'),
        'title': 'Realme 65W SuperDart Fast Charger with Yellow Cable',
        'description': 'Found a white Realme adapter with signature yellow Type-C cable plugged into the power socket in Room 312, Sir MV Block.',
        'type': 'found',
        'category': 'Electronics',
        'location': 'Main Building',
        'date_lost_found': now - timedelta(days=1),
        'image_url': '',
        'status': 'active',
        'created_by': _sinchana,
        'created_at': now - timedelta(days=1),
        'updated_at': now - timedelta(days=1)
    },
    {
        '_id': ObjectId('6724ed010000000000000009'),
        'title': 'Noise ColorFit Pulse Smartwatch (Black Strap)',
        'description': 'Lost my smartwatch on the outdoor basketball court during the evening match. Screen protector has minor air bubble on top-right edge.',
        'type': 'lost',
        'category': 'Accessories',
        'location': 'Sports Complex',
        'date_lost_found': now - timedelta(days=2),
        'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
        'status': 'active',
        'created_by': _likith,
        'created_at': now - timedelta(days=2),
        'updated_at': now - timedelta(days=2)
    },
    {
        '_id': ObjectId('6724ed01000000000000000a'),
        'title': 'Spectacles with Matte Black Frame (Lenskart Air)',
        'description': 'Found reading glasses in a hard blue case left on the counter of Gokulam Campus Canteen juice shop.',
        'type': 'found',
        'category': 'Accessories',
        'location': 'Cafeteria',
        'date_lost_found': now - timedelta(hours=18),
        'image_url': 'https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=500',
        'status': 'active',
        'created_by': _varsha,
        'created_at': now - timedelta(hours=18),
        'updated_at': now - timedelta(hours=18)
    },
    {
        '_id': ObjectId('6724ed01000000000000000b'),
        'title': 'Data Structures Lab Record (Handwritten with Diagrams)',
        'description': 'Lost blue hardbound DS Record Notebook before lab external submission. Last seen near EC Dept HOD office corridor. Very urgent!',
        'type': 'lost',
        'category': 'Books and Notes',
        'location': 'Lab Block',
        'date_lost_found': now - timedelta(days=1),
        'image_url': '',
        'status': 'active',
        'created_by': _tejaswini,
        'created_at': now - timedelta(days=1),
        'updated_at': now - timedelta(days=1)
    },
    {
        '_id': ObjectId('6724ed01000000000000000c'),
        'title': 'Yamaha FZ-S Bike Key with Royal Enfield Fabric Tag',
        'description': 'Found single bike key near VVCE Main Gate entry ramp. Red Royal Enfield "Made Like a Gun" fabric tag attached.',
        'type': 'found',
        'category': 'Keys',
        'location': 'Parking Area',
        'date_lost_found': now - timedelta(days=3),
        'image_url': '',
        'status': 'active',
        'created_by': _prajwal,
        'created_at': now - timedelta(days=3),
        'updated_at': now - timedelta(days=3)
    },
    {
        '_id': ObjectId('6724ed01000000000000000d'),
        'title': 'OnePlus Nord CE 3 (Aqua Surge Color)',
        'description': 'Lost my OnePlus phone with transparent case and sticker of Royal Challengers Bangalore (RCB). Lost near Auditorium stage.',
        'type': 'lost',
        'category': 'Mobile Phones',
        'location': 'Auditorium',
        'date_lost_found': now - timedelta(days=5),
        'image_url': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500',
        'status': 'active',
        'created_by': _darshan,
        'created_at': now - timedelta(days=5),
        'updated_at': now - timedelta(days=5)
    },
    {
        '_id': ObjectId('6724ed01000000000000000e'),
        'title': 'Milton Thermosteel 1000ml Bottle (Matte Blue)',
        'description': 'Found blue insulated Milton water bottle in Badminton Court viewing gallery after college sports practice.',
        'type': 'found',
        'category': 'Other',
        'location': 'Sports Complex',
        'date_lost_found': now - timedelta(days=2),
        'image_url': '',
        'status': 'active',
        'created_by': _spandana,
        'created_at': now - timedelta(days=2),
        'updated_at': now - timedelta(days=2)
    },
    {
        '_id': ObjectId('6724ed01000000000000000f'),
        'title': 'SanDisk Ultra Dual 64GB Pendrive (Type-C & Type-A)',
        'description': 'Silver metallic USB drive lost in Seminar Hall 2 during 8th semester Major Project PPT review. Contains project source code.',
        'type': 'lost',
        'category': 'Electronics',
        'location': 'Auditorium',
        'date_lost_found': now - timedelta(days=3),
        'image_url': '',
        'status': 'active',
        'created_by': _rohith,
        'created_at': now - timedelta(days=3),
        'updated_at': now - timedelta(days=3)
    },
    {
        '_id': ObjectId('6724ed010000000000000010'),
        'title': 'Yonex Nanoray 70 Light Badminton Racket',
        'description': 'Found Yonex racket in full black cover inside Indoor Gymnasium locker area. Left behind on Saturday morning.',
        'type': 'found',
        'category': 'Other',
        'location': 'Sports Complex',
        'date_lost_found': now - timedelta(days=4),
        'image_url': '',
        'status': 'claimed',
        'created_by': _chethan,
        'created_at': now - timedelta(days=4),
        'updated_at': now - timedelta(days=1)
    },
    {
        '_id': ObjectId('6724ed010000000000000011'),
        'title': 'Redmi Note 12 5G (Frosted Green)',
        'description': 'Found a green Redmi phone on bench near Sir MV statue. Locked with pattern. Battery was at 45% when found.',
        'type': 'found',
        'category': 'Mobile Phones',
        'location': 'Main Building',
        'date_lost_found': now - timedelta(hours=6),
        'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500',
        'status': 'active',
        'created_by': _sinchana,
        'created_at': now - timedelta(hours=6),
        'updated_at': now - timedelta(hours=6)
    },
    {
        '_id': ObjectId('6724ed010000000000000012'),
        'title': 'Titan Karishma Analog Watch (Golden Dial)',
        'description': 'Lost classic Titan watch with brown leather strap in Admin Block fee counter queue. Family gift with sentimental value.',
        'type': 'lost',
        'category': 'Accessories',
        'location': 'Admin Block',
        'date_lost_found': now - timedelta(days=6),
        'image_url': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=500',
        'status': 'active',
        'created_by': _varsha,
        'created_at': now - timedelta(days=6),
        'updated_at': now - timedelta(days=6)
    },
    {
        '_id': ObjectId('6724ed010000000000000013'),
        'title': 'Mechanical Engineering Mini Drafter with Canvas Cover',
        'description': 'Found Omega brand mini drafter in Chennaiah Mechanical Workshop drawing hall. Initials "K.M." etched on ruler.',
        'type': 'found',
        'category': 'Other',
        'location': 'Lab Block',
        'date_lost_found': now - timedelta(days=3),
        'image_url': '',
        'status': 'returned',
        'created_by': _likith,
        'created_at': now - timedelta(days=3),
        'updated_at': now - timedelta(hours=4)
    },
    {
        '_id': ObjectId('6724ed010000000000000014'),
        'title': 'Black Nike Dri-FIT Sports Zipper Jacket',
        'description': 'Left black Nike hoodie jacket on bleachers of college football ground after inter-branch tournament match.',
        'type': 'lost',
        'category': 'Clothing',
        'location': 'Sports Complex',
        'date_lost_found': now - timedelta(days=5),
        'image_url': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=500',
        'status': 'active',
        'created_by': _prajwal,
        'created_at': now - timedelta(days=5),
        'updated_at': now - timedelta(days=5)
    },
    {
        '_id': ObjectId('6724ed010000000000000015'),
        'title': 'Ladies Leather Handbag (Maroon Color)',
        'description': 'Found maroon handbag on sofa in Placement Cell waiting lobby. Contains cosmetics, notebook, and college syllabus copy.',
        'type': 'found',
        'category': 'Bags',
        'location': 'Admin Block',
        'date_lost_found': now - timedelta(days=2),
        'image_url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=500',
        'status': 'active',
        'created_by': _tejaswini,
        'created_at': now - timedelta(days=2),
        'updated_at': now - timedelta(days=2)
    },
    {
        '_id': ObjectId('6724ed010000000000000016'),
        'title': 'Apple AirPods Pro (2nd Gen) in MagSafe Case',
        'description': 'Lost AirPods Pro near Gokulam 3rd stage auto stand just outside VVCE college campus gate. Case has a spigen black bumper sleeve.',
        'type': 'lost',
        'category': 'Electronics',
        'location': 'Other',
        'date_lost_found': now - timedelta(days=1),
        'image_url': 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500',
        'status': 'active',
        'created_by': _ananya,
        'created_at': now - timedelta(days=1),
        'updated_at': now - timedelta(days=1)
    },
    {
        '_id': ObjectId('6724ed010000000000000017'),
        'title': 'Tupperware Lunch Bag with 3 Steel Dabbas',
        'description': 'Found red insulated lunch tote bag on stone bench near civil dept water cooler. Handed to security office.',
        'type': 'found',
        'category': 'Other',
        'location': 'Main Building',
        'date_lost_found': now - timedelta(hours=10),
        'image_url': '',
        'status': 'returned',
        'created_by': _darshan,
        'created_at': now - timedelta(hours=10),
        'updated_at': now - timedelta(hours=2)
    }
]

FALLBACK_CLAIMS = [
    {
        '_id': ObjectId('6724ee010000000000000001'),
        'item_id': ObjectId('6724ed010000000000000010'),
        'requester_id': _prajwal,
        'message': 'This is my Yonex racket, I left it in the gym locker Saturday morning.',
        'status': 'approved',
        'created_at': now - timedelta(days=1),
        'updated_at': now - timedelta(days=1)
    }
]

# ── Helper functions for seamless offline/in-memory operation ──

def get_fallback_stats():
    total = len(FALLBACK_ITEMS)
    lost = sum(1 for i in FALLBACK_ITEMS if i.get('type') == 'lost')
    found = sum(1 for i in FALLBACK_ITEMS if i.get('type') == 'found')
    returned = sum(1 for i in FALLBACK_ITEMS if i.get('status') == 'returned')
    return {'total': total, 'lost': lost, 'found': found, 'returned': returned}

def get_fallback_recent(item_type, limit=6):
    items = [i for i in FALLBACK_ITEMS if i.get('type') == item_type and i.get('status') == 'active']
    items.sort(key=lambda x: x.get('created_at', now), reverse=True)
    return items[:limit]

def filter_fallback_items(q=None, item_type=None, category=None, location=None, status=None, sort='newest'):
    results = list(FALLBACK_ITEMS)
    if status:
        results = [i for i in results if i.get('status') == status]
    if item_type:
        results = [i for i in results if i.get('type') == item_type]
    if category:
        results = [i for i in results if i.get('category') == category]
    if location:
        results = [i for i in results if i.get('location') == location]
    if q:
        ql = q.lower()
        results = [i for i in results if ql in i.get('title', '').lower() or ql in i.get('description', '').lower()]
    
    if sort == 'oldest':
        results.sort(key=lambda x: x.get('created_at', now))
    else:
        results.sort(key=lambda x: x.get('created_at', now), reverse=True)
    return results

def get_fallback_item(item_id):
    for i in FALLBACK_ITEMS:
        if str(i['_id']) == str(item_id):
            return i
    return None

def add_fallback_item(item_dict):
    if '_id' not in item_dict:
        item_dict['_id'] = ObjectId()
    if 'created_at' not in item_dict:
        item_dict['created_at'] = datetime.now(timezone.utc)
    if 'updated_at' not in item_dict:
        item_dict['updated_at'] = datetime.now(timezone.utc)
    FALLBACK_ITEMS.insert(0, item_dict)
    return item_dict['_id']

def get_fallback_user_by_id(uid):
    for u in FALLBACK_USERS:
        if str(u['_id']) == str(uid):
            return u
    return None

def get_fallback_user_by_email(email):
    for u in FALLBACK_USERS:
        if u['email'].lower() == (email or '').lower():
            return u
    return None

def add_fallback_user(user_dict):
    if '_id' not in user_dict:
        user_dict['_id'] = ObjectId()
    if 'created_at' not in user_dict:
        user_dict['created_at'] = datetime.now(timezone.utc)
    FALLBACK_USERS.append(user_dict)
    return user_dict['_id']
