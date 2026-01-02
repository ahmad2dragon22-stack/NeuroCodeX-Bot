import json
import os
from datetime import datetime
from config.settings import DB_FILE

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "users": {},
        "public_store": [],
        "official_store": [],
        "settings": {"active_contests": 0},
        "stats": {"total_events": 0, "total_users": 0, "total_transfers": 0}
    }

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def get_user(user_id, username="Guest"):
    user_id = str(user_id)
    db = load_db()
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "points": 0,
            "username": username,
            "referred_by": None,
            "referrals": 0,
            "items_sold": 0,
            "joined_at": str(datetime.now()),
            "last_active": str(datetime.now())
        }
        db["stats"]["total_users"] += 1
        save_db(db)
    return db["users"][user_id]

def update_user(user_id, updates):
    db = load_db()
    user_id = str(user_id)
    if user_id in db["users"]:
        db["users"][user_id].update(updates)
        db["users"][user_id]["last_active"] = str(datetime.now())
        save_db(db)

def add_points(user_id, points):
    db = load_db()
    user_id = str(user_id)
    if user_id in db["users"]:
        db["users"][user_id]["points"] += points
        save_db(db)

def get_stats():
    db = load_db()
    return db["stats"]

def update_stats(key, value):
    db = load_db()
    db["stats"][key] = value
    save_db(db)