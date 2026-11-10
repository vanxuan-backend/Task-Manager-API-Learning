from fastapi import FastAPI
from v2_sqlite_database.database import create_tables

app = FastAPI()
@app.on_event("startup")
def startup_event():
    create_tables()

@app.get("/")
def read_root():
    return {"message": "Task Manager API 2.0"}