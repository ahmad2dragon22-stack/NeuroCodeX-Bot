#!/usr/bin/env python3
"""
سكريبت النسخ الاحتياطي لقاعدة البيانات
"""
import os
import shutil
from datetime import datetime
from config.settings import DB_FILE

def backup_database():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    if not os.path.exists(DB_FILE):
        print("❌ قاعدة البيانات غير موجودة!")
        return False

    # إنشاء مجلد النسخ الاحتياطية
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    # اسم الملف مع التاريخ
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/dragon_db_{timestamp}.json"

    # نسخ الملف
    shutil.copy2(DB_FILE, backup_file)

    print(f"✅ تم إنشاء النسخة الاحتياطية: {backup_file}")
    return True

def list_backups():
    """عرض قائمة بالنسخ الاحتياطية"""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        print("لا توجد نسخ احتياطية")
        return

    backups = [f for f in os.listdir(backup_dir) if f.startswith("dragon_db_")]
    backups.sort(reverse=True)

    print("📁 النسخ الاحتياطية المتاحة:")
    for backup in backups[:10]:  # أحدث 10
        print(f"  - {backup}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_backups()
    else:
        backup_database()