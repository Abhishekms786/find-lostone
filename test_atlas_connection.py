"""
test_atlas_connection.py - Verifies MongoDB Atlas connectivity and CRUD operations.
Never logs or exposes credentials.
"""
import os
import sys
import re
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI', '')
DB_NAME = os.environ.get('DB_NAME', 'findit_db')

def mask_uri(uri):
    return re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', uri)

def run_test():
    if not MONGO_URI:
        print("[FAIL] MONGO_URI is not set in .env")
        return False

    if not MONGO_URI.startswith('mongodb+srv://') and 'mongodb.net' not in MONGO_URI:
        print("[STATUS] MONGO_URI in .env is currently pointing to local MongoDB:")
        print(f"         {mask_uri(MONGO_URI)}")
        print("         To connect to Atlas, update .env with your Atlas credentials:")
        print("         MONGO_URI=mongodb+srv://<username>:<password>@cluster0.lpiqcbo.mongodb.net/findit_db?retryWrites=true&w=majority")
        return False

    print(f"[1/6] Attempting connection to MongoDB Atlas ({mask_uri(MONGO_URI)})...")
    try:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=8000,
            connectTimeoutMS=8000,
            socketTimeoutMS=8000
        )
        # Step 2: Ping
        client.admin.command('ping')
        print("[2/6] Ping verified successfully! Connection established with Atlas Cluster0.")
    except Exception as exc:
        print(f"[FAIL] Could not connect to Atlas: {exc}")
        return False

    # Step 3: Select DB
    db = client[DB_NAME]
    print(f"[3/6] Target database selected: {db.name}")

    # Step 4: Ensure collections exist
    existing_collections = db.list_collection_names()
    print(f"       Existing collections in {db.name}: {existing_collections}")
    for col_name in ['users', 'items', 'claims']:
        if col_name not in existing_collections:
            db.create_collection(col_name)
            print(f"       Created collection: {col_name}")
    print("[4/6] Collections verified: users, items, claims")

    # Step 5 & 6 & 7: Insert, read back, delete temporary test document
    print("[5/6] Inserting temporary verification document...")
    test_doc = {
        '_test_marker': 'atlas_verification_check',
        'timestamp': datetime.now(timezone.utc),
        'note': 'Temporary test document to verify Atlas write and read persistence.'
    }
    insert_result = db.items.insert_one(test_doc)
    doc_id = insert_result.inserted_id
    print(f"       Inserted test document ID: {doc_id}")

    print("[6/6] Reading back and verifying persistence...")
    read_doc = db.items.find_one({'_id': doc_id})
    if not read_doc or read_doc.get('_test_marker') != 'atlas_verification_check':
        print("[FAIL] Readback verification failed.")
        return False
    print("       Readback successful: document matched.")

    # Delete test document
    db.items.delete_one({'_id': doc_id})
    confirm_deleted = db.items.find_one({'_id': doc_id})
    if confirm_deleted is not None:
        print("[FAIL] Document deletion failed.")
        return False
    print("       Test document deleted cleanly.")

    print("\n[SUCCESS] MongoDB Atlas connection and read/write persistence verified 100%!")
    return True

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)
