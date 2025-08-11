# app/database.py
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def create_connection():
    """ 创建到MySQL数据库的数据库连接 """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"连接到MySQL时出错：{e}")
        return None

@contextmanager
def get_db_connection():
    """处理数据库连接的上下文管理器。"""
    connection = create_connection()
    if connection is None:
        raise IOError("无法连接到数据库。")
    try:
        yield connection
    finally:
        if connection.is_connected():
            connection.close()

@contextmanager
def get_db_cursor(commit=False):
    """处理数据库游标的上下文管理器，可选择提交。"""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True) # dictionary=True to get results as dicts
        try:
            yield cursor
        except Error as e:
            print(f"数据库错误：{e}")
            conn.rollback()
            raise
        else:
            if commit:
                conn.commit()
        finally:
            cursor.close()

# 使用示例：
#
# with get_db_cursor() as cursor:
#     cursor.execute("SELECT * FROM projects")
#     projects = cursor.fetchall()
#
# with get_db_cursor(commit=True) as cursor:
#     cursor.execute("INSERT INTO projects (name) VALUES (%s)", ("New Project",))
#
