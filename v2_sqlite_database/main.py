from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
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
    return {"message": "Task Manager API 2.5"}

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
def get_tasks(
    completed: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):

    conn = get_db_connection()
    cursor = conn.cursor()
    
    query_conditions = []
    params = []
    
    if completed is not None:
        query_conditions.append("completed = ?")
        params.append(completed)
    
    if search is not None:
        #LIKE演算子と「%」ワイルドカードを使用して、指定したキーワードを含む文字列を検索する。
        query_conditions.append("title LIKE ?")
        params.append(f"%{search}%")
    
    where_clause = ""
    if query_conditions:
        where_clause = "WHERE " + " AND ".join(query_conditions)
        
    #COUNT(*)を使用して、データを取得せずにレコード数を効率的にカウントする。
    count_query = f"SELECT COUNT(*) FROM tasks {where_clause}"
    cursor.execute(count_query, params)
    total_records = cursor.fetchone()[0]
    
    #LIMITは取得するレコードの最大件数を指定し、OFFSETは取得対象から除外するレコード数を指定する。
    data_query = f"SELECT * FROM tasks {where_clause} LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    cursor.execute(data_query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "total": total_records,
        "skip": skip,
        "limit": limit,
        "search_keyword": search,
        "tasks": [dict(row) for row in rows]
    }
    
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
    
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    ## SQL文内の「?」の順序は、下記のタプル内の変数の順序と一致させる。
    cursor.execute(
        "UPDATE tasks SET title = ?, completed = ? WHERE id = ?", 
        (updated_task.title, updated_task.completed, task_id)
    )
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()
    
    #影響を受けた行がない場合、指定されたIDのデータは存在しない。
    if updated_rows == 0:
        raise HTTPException(status_code=404, detail="タスクが見つかりませんでした。")
    
    return {
        "message": f"ID {task_id} のタスクを正常に更新しました。",
        "task": {
            "id": task_id,
            "title": updated_task.title,
            "completed": updated_task.completed
        }
    }

