from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from v2_sqlite_database.database import create_tables, get_db_connection

app = FastAPI()
@app.on_event("startup")
def startup_event():
    create_tables()

#バージョン1.6からのデータバリデーションロジック
class TaskCreate(BaseModel):
    title: str = Field(..., min_length = 1, max_length = 100)
    completed: bool = Field(default=False)

@app.get("/")
def read_root():
    return {"message": "Task Manager API 2.3"}

@app.post("/tasks")
def create_task(task: TaskCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    #SQLインジェクションを防止するためにパラメータ化クエリを使用する
    cursor.execute(
        "INSERT INTO tasks (title, completed) VALUES (?, ?)", 
        (task.title, task.completed)
    )
    #ハードディスクへの保存
    conn.commit()
    
    #IDを取得し、自動的にインクリメントする
    new_task_id = cursor.lastrowid
    cursor.close()
    
    return {
        "message": "タスクをデータベースに保存しました！",
        "task": {
            "id": new_task_id,
            "title": task.title,
            "completed": task.completed
        }
    }
    
@app.get("/tasks")
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    #SQLのSELECT *文を使用して、tasksテーブルの全カラムを取得する。
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    tasks = [dict(row) for row in rows]
    return {"tasks": tasks}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    #SELECT文とWHERE句を組み合わせて、IDを指定してデータを検索する。
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone() #該当するデータが存在する場合、1件のみ取得する。
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail="タスクが見つかりませんでした。")
    
    return {"tasks": dict(row)}
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    #DELETE文とWHERE句を組み合わせて、IDを指定してデータを削除する。
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()
    
    if deleted_rows == 0:
        raise HTTPException(status_code=404, detail="タスクが見つかりませんでした。")
    
    return {"message": f"ID {task_id} のタスクを正常に削除しました。"}
    
