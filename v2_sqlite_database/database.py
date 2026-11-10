import sqlite3

DB_NAME = "tasks.db"

def get_db_connection():
    #データベースファイルへの接続
    conn = sqlite3.connect(DB_NAME, check_same_thread = False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    #tasks テーブルが存在しない場合に作成する
    conn = get_db_connection()
    cursor = conn.cursor()
    
    #テーブル作成用のSQL文
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    