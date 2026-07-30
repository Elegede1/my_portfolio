"""
Admin account helper for the portfolio.

There is no public sign-up route: the admin dashboard at
    /12812673-738234login  ->  /12812673-738234admin
only lets in a user whose `role` is "admin". This script creates (or promotes,
or resets the password of) that admin user directly in MongoDB, using the same
MONGO_URI and password hashing (werkzeug) as the app.

Usage (from the project root, with MONGO_URI set in your .env or environment):

    # interactive (prompts for details, hides password input)
    python create_admin.py

    # non-interactive
    python create_admin.py --email you@example.com --name "Jekuthiel Okafor" --password "SuperSecret123"

    # just list existing users
    python create_admin.py --list
"""
import argparse
import getpass
import os
import sys

from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash


def get_db():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("mongo_uri")
    if not mongo_uri:
        print("ERROR: MONGO_URI is not set (put it in your .env or environment).")
        sys.exit(1)
    mongo_uri = mongo_uri.strip().replace("/?", "?")
    if mongo_uri.endswith("/"):
        mongo_uri = mongo_uri[:-1]
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=8000)
    # Surface connection problems early with a clear message.
    client.admin.command("ping")
    return client.get_default_database()


def list_users(db):
    users = list(db.users.find())
    if not users:
        print("No users found.")
        return
    print(f"{'EMAIL':40} {'NAME':25} ROLE")
    print("-" * 75)
    for u in users:
        print(f"{u.get('email',''):40} {u.get('name',''):25} {u.get('role','')}")


def upsert_admin(db, email, name, password):
    email = email.strip().lower()
    hashed = generate_password_hash(password)  # PBKDF2 by default; matches app's check_password_hash
    existing = db.users.find_one({"email": email})
    if existing:
        db.users.update_one(
            {"_id": existing["_id"]},
            {"$set": {"name": name, "password": hashed, "role": "admin"}},
        )
        print(f"Updated existing user '{email}' -> role=admin, password reset.")
    else:
        db.users.insert_one(
            {"email": email, "name": name, "password": hashed, "role": "admin"}
        )
        print(f"Created new admin user '{email}'.")
    print("\nYou can now log in at:  /12812673-738234login")
    print("Then you'll be redirected to:  /12812673-738234admin")


def main():
    parser = argparse.ArgumentParser(description="Create or update the portfolio admin user.")
    parser.add_argument("--email")
    parser.add_argument("--name")
    parser.add_argument("--password")
    parser.add_argument("--list", action="store_true", help="List existing users and exit.")
    args = parser.parse_args()

    db = get_db()

    if args.list:
        list_users(db)
        return

    email = args.email or input("Admin email: ").strip()
    name = args.name or input("Display name: ").strip()
    password = args.password or getpass.getpass("Password: ")
    if not (email and name and password):
        print("ERROR: email, name and password are all required.")
        sys.exit(1)

    upsert_admin(db, email, name, password)


if __name__ == "__main__":
    main()
