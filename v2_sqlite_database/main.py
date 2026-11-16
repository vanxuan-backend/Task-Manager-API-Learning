from fastapi import FastAPI
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
    return {"message": "Task Manager API 2.1"}

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