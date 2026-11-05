from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 一時データ（サーバーを停止すると消失します）
tasks = [
    {"id": 1, "title": "簡単Task Manager API", "completed": False},
    {"id": 2, "title": "Task Manager API 1.0.0", "completed": False}
]

# 入力データ構造の定義
class Task(BaseModel):
    id: int
    title: str
    completed: bool = False
    
@app.get("/")
def read_root():
    return {"message": "こんにちは"}

# 全タスク一覧の取得
@app.get("/tasks")
def get_tasks():
    return {"tasks": tasks}

# 新しいタスクを追加する
@app.post("/tasks")
def create_task(task: Task):
    new_task = task.model_dump()
    tasks.append(new_task)
    return {
        "message" : "タスクを追加しました！"
    }
    
# タスクIDでタスクを取得する
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return {"task": task}
    return {"message": "タスクが見つかりませんでした。"}