import sqlite3
from pathlib import Path

from pymongo import MongoClient
from datetime import datetime

# 获取当前脚本的绝对路径
sqlite_file = Path("jrrpdata.db").absolute()

# 打印路径以确保正确
print(f"使用数据库路径: {sqlite_file}")

# 连接到 SQLite 数据库
sqlite_db = sqlite3.connect(str(sqlite_file))
sqlite_cursor = sqlite_db.cursor()

# 连接到 MongoDB
mongo_client = MongoClient(
    "192.168.100.220", 27017, unicode_decode_error_handler='ignore')
mongo_db = mongo_client['JuJiuBot']
jdata_collection = mongo_db['jrrp']


# MongoDB 插入逻辑函数（嵌套结构）
def insert_tb(qqid, value, date):
    # 更新该用户的日期记录，如果该日期的记录已经存在则更新，否则追加
    jdata_collection.update_one(
        {"qid": qqid, "records.time": date},
        {"$set": {"records.$.value": value}},  # 更新该日期的记录
        upsert=False
    )

    # 如果没有该日期的记录，则追加新日期记录
    jdata_collection.update_one(
        {"qid": qqid, "records.time": {"$ne": date}},  # 如果记录中没有该日期
        {"$push": {"records": {"time": date, "value": value}}},  # 追加新的日期记录
        upsert=True  # 如果没有该用户则插入新文档
    )


# 从 SQLite 读取所有数据
sqlite_cursor.execute("SELECT QQID, Value, Date FROM jdata")
rows = sqlite_cursor.fetchall()

# 遍历 SQLite 数据并插入 MongoDB
for row in rows:
    qqid = row[0]
    value = row[1]
    date_str = row[2]

    # 确保日期是合适的格式（如 "240920" -> "24-09-2020"）
    try:
        date = datetime.strptime(date_str, '%y%m%d').strftime('%y%m%d')
    except ValueError as e:
        print(f"错误的日期格式，跳过: {row}")
        continue

    # 插入到 MongoDB
    insert_tb(str(qqid), value, date)

# 完成后关闭 SQLite 数据库连接
sqlite_db.close()
mongo_client.close()

print("数据迁移完成。")
