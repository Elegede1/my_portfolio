import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv('MONGO_URI') or os.getenv('mongo_uri')
if not mongo_uri:
    print("MONGO_URI not found")
    exit()
mongo_uri = mongo_uri.strip().replace('/?', '?')
if mongo_uri.endswith('/'): mongo_uri = mongo_uri[:-1]

client = MongoClient(mongo_uri)
db = client.get_default_database()

print('--- Skills ---')
for s in db.skills.find():
    print(f"{s.get('name')} | {s.get('skill_type')}")

print('--- Education ---')
for e in db.education.find():
    print(f"{e.get('institution')} | {e.get('degree')}")
