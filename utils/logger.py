import logging
import os
from datetime import datetime

def setup_logger(name="dragon_bot", level=logging.INFO):
    """إعداد نظام السجلات"""

    # إنشاء مجلد السجلات
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # اسم الملف مع التاريخ
    log_file = f"{log_dir}/{name}_{datetime.now().strftime('%Y%m%d')}.log"

    # إعداد التنسيق
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # إعداد المعالج للملف
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # إعداد المعالج للكونسول
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # إعداد السجل
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# سجل عام للبوت
bot_logger = setup_logger()