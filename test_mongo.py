"""
Diagnostic script to test MongoDB Atlas connection and inspect collections.
Usage: python test_mongo.py
"""
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

# Configure dnspython nameservers
try:
    import dns.resolver
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
except Exception:
    pass

load_dotenv()

mongo_uri = os.getenv('MONGO_URI')
db_name = os.getenv('DB_NAME', 'findit_db')

print("=" * 60)
print("FindIt - MongoDB Atlas Connection Diagnostic")
print("=" * 60)

if not mongo_uri:
    print("[ERROR] MONGO_URI is not set in .env")
    sys.exit(1)

import re
masked_uri = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', mongo_uri)
print(f"Connecting to: {masked_uri}")
print(f"Target Database: {db_name}")

# Get public IP
try:
    import urllib.request
    current_ip = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode().strip()
    print(f"Your Current Public IP: {current_ip}")
except Exception:
    current_ip = "Unknown"

print("\nAttempting connection with certifi CA bundle...")
try:
    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=6000,
        connectTimeoutMS=6000,
        socketTimeoutMS=6000,
        tlsCAFile=certifi.where()
    )
    res = client.admin.command('ping')
    print("[SUCCESS] Ping Successful! MongoDB responded:", res)

    db = client[db_name]
    collections = db.list_collection_names()
    print(f"\n[OK] Connected to database '{db_name}'. Collections: {collections}")

    for coll_name in ['items', 'users', 'claims']:
        if coll_name in collections:
            count = db[coll_name].count_documents({})
            print(f"  * {coll_name}: {count} documents")
        else:
            print(f"  * {coll_name}: (collection not created yet)")

    print("\n[SUCCESS] Everything is working! New items will save directly to MongoDB Atlas.")

except Exception as exc:
    err_str = str(exc)
    print("\n[FAILED] Connection Failed!")
    print(f"Error Details: {err_str}")

    if "TLSV1_ALERT_INTERNAL_ERROR" in err_str or "ServerSelectionTimeoutError" in err_str:
        print("\n" + "=" * 60)
        print(">> ROOT CAUSE: IP ADDRESS NOT WHITELISTED IN MONGODB ATLAS <<")
        print("=" * 60)
        print(f"Your current public IP is: {current_ip}")
        print("\nTo fix this in 30 seconds:")
        print("1. Go to https://cloud.mongodb.com and log in.")
        print("2. In the left sidebar under 'SECURITY', click 'Network Access'.")
        print("3. Click '+ ADD IP ADDRESS'.")
        print("4. Click 'ALLOW ACCESS FROM ANYWHERE' (0.0.0.0/0).")
        print("5. Click 'Confirm'.")
        print("6. Run 'python test_mongo.py' again. Once connected, your data will save to MongoDB!")
        print("=" * 60)
