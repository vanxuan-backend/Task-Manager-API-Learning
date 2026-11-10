from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from pydantic import Field

app = FastAPI()

# 一時データ（サーバーを停止すると消失します）
tasks = [
    {"id": 1, "title": "簡単Task Manager API", "completed": False},
    {"id": 2, "title": "Task Manager API 1.8", "completed": False}
]

# 入力データ構造の定義
class Task(BaseModel):
    id: int
    title: str = Field(..., min_length=3, max_length=100, description="タスクのタイトル（3文字以上、100文字以下）")
    completed: bool = False
    
@app.get("/")
def read_root():
    raise HTTPException(status_code=200, detail="こんにちは")

# タスク一覧取得 - 絞り込み機能
@app.get("/tasks")
def get_tasks(completed: Optional[bool] = None):
    # completed パラメータが指定されていない場合、すべてのタスクを返す。
    if completed is None:
        raise HTTPException(status_code=200, detail={"tasks": tasks})

    # completed パラメータが指定されている場合、リスト内包表記（List Comprehension）を使用して、条件に一致するタスクを抽出する。
    filtered_tasks = [task for task in tasks if task["completed"] == completed]
    raise HTTPException(status_code=200, detail={"tasks": filtered_tasks})

# 新しいタスクを追加する
@app.post("/tasks")
def create_task(task: Task):
    new_task = task.model_dump()
    tasks.append(new_task)
    raise HTTPException(status_code=201, detail="タスクを追加しました！")

# タスクのフィルタリングとページネーション
@app.get("/tasks/{task_id}")
def get_task(
    completed: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
    ):
    
    filtered_tasks = tasks
    # 完了状態によるフィルタリング
    if completed is not None:
        filtered_tasks = [task for task in tasks if task["completed"] == completed]
        
    #キーワードによるテキスト検索
    if search is not None:
        filtered_tasks = [task for task in filtered_tasks if search.lower() in task["title"].lower()]
    #スライシングによるページネーション (Pagination)
    paginated_tasks = filtered_tasks[skip : skip +limit]
    
    return {
        "total" : len(filtered_tasks),
        "skip" : skip,
        "limit" : limit,
        "tasks" : paginated_tasks
    }
# タスクIDでタスクを削除する
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            del tasks[index]
            raise HTTPException(status_code=200, detail="タスクを削除しました！")
    raise HTTPException(status_code=404, detail="タスクが見つかりませんでした。")

# タスクIDでタスクを更新する
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks[index] = updated_task.model_dump()
            raise HTTPException(status_code=200, detail="タスクを更新しました！")
    raise HTTPException(status_code=404, detail="タスクが見つかりませんでした。")