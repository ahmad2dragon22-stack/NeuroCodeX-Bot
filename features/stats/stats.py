from datetime import datetime, timedelta
from database.db_manager import load_db, get_user
from utils.helpers import format_number, calculate_level

def get_user_stats(user_id):
    """الحصول على إحصائيات مفصلة للمستخدم"""
    db = load_db()
    user = db["users"].get(str(user_id), {})

    if not user:
        return None

    # حساب النشاط
    joined_date = datetime.fromisoformat(user.get("joined_at", str(datetime.now())))
    days_since_join = (datetime.now() - joined_date).days

    # حساب متوسط النقاط يومياً
    daily_avg = user["points"] / max(days_since_join, 1)

    # حساب المستوى التالي
    current_level = calculate_level(user["points"])
    next_level_points = get_next_level_points(current_level)

    return {
        "points": user["points"],
        "level": current_level,
        "referrals": user["referrals"],
        "items_sold": user["items_sold"],
        "joined_days": days_since_join,
        "daily_avg": round(daily_avg, 2),
        "next_level_points": next_level_points,
        "progress_percent": min(100, (user["points"] / next_level_points) * 100) if next_level_points > 0 else 100
    }

def get_next_level_points(current_level):
    """حساب النقاط المطلوبة للمستوى التالي"""
    if current_level < 10:
        return current_level * 100
    elif current_level < 20:
        return (current_level - 9) * 500 + 1000
    else:
        return (current_level - 19) * 1000 + 10000

def get_global_stats():
    """الحصول على الإحصائيات العامة المفصلة"""
    db = load_db()
    users = db["users"]
    stats = db["stats"]

    total_points = sum(user["points"] for user in users.values())
    active_users = sum(1 for user in users.values() if user.get("last_active"))

    # حساب متوسط النقاط لكل مستخدم
    avg_points_per_user = total_points / max(len(users), 1)

    # أفضل المستخدمين
    top_users = sorted(users.items(), key=lambda x: x[1]["points"], reverse=True)[:10]

    return {
        "total_users": stats["total_users"],
        "total_events": stats["total_events"],
        "total_transfers": stats["total_transfers"],
        "total_points": total_points,
        "active_users": active_users,
        "avg_points_per_user": round(avg_points_per_user, 2),
        "public_store_items": len(db["public_store"]),
        "official_store_items": len(db["official_store"]),
        "top_users": top_users
    }

def get_leaderboard(limit=10):
    """الحصول على لوحة الصدارة"""
    db = load_db()
    users = db["users"]

    leaderboard = []
    for user_id, user_data in users.items():
        leaderboard.append({
            "user_id": user_id,
            "username": user_data.get("username", "غير معروف"),
            "points": user_data["points"],
            "level": calculate_level(user_data["points"]),
            "referrals": user_data["referrals"]
        })

    return sorted(leaderboard, key=lambda x: x["points"], reverse=True)[:limit]

def get_activity_stats(days=7):
    """إحصائيات النشاط خلال فترة معينة"""
    db = load_db()
    users = db["users"]

    cutoff_date = datetime.now() - timedelta(days=days)
    active_in_period = 0
    new_users = 0

    for user in users.values():
        last_active = user.get("last_active")
        if last_active:
            last_active_date = datetime.fromisoformat(last_active)
            if last_active_date >= cutoff_date:
                active_in_period += 1

        joined_date = datetime.fromisoformat(user.get("joined_at", str(datetime.now())))
        if joined_date >= cutoff_date:
            new_users += 1

    return {
        "active_users": active_in_period,
        "new_users": new_users,
        "period_days": days
    }