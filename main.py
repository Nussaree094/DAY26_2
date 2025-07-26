from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import date, datetime
from typing import List
import pytz  # ✅ ใช้สำหรับแปลงเวลาเป็นเวลาไทย

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Timezone ของไทย
bangkok = pytz.timezone("Asia/Bangkok")

# Pydantic model
class Todo(BaseModel):
    id: int
    task: str
    due: date
    created_at: datetime
    updated_at: datetime

# Memory storage
todos: List[Todo] = []
current_id = 1

@app.get("/", response_class=HTMLResponse)
def read_all(request: Request):
    today_str = date.today().isoformat()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "todos": todos,
        "today": today_str
    })

@app.post("/create-todo")
def create_todo(task: str = Form(...), due: date = Form(...)):
    global current_id
    now = datetime.now(bangkok)
    todos.append(Todo(
        id=current_id,
        task=task,
        due=due,
        created_at=now,
        updated_at=now
    ))
    current_id += 1
    return RedirectResponse("/", status_code=303)

@app.post("/delete-todo/{todo_id}")
def delete_todo(todo_id: int):
    global todos
    todos = [todo for todo in todos if todo.id != todo_id]
    return RedirectResponse("/", status_code=303)

@app.post("/edit-todo/{todo_id}")
def edit_todo(todo_id: int, task: str = Form(...), due: date = Form(...)):
    now = datetime.now(bangkok)
    for todo in todos:
        if todo.id == todo_id:
            todo.task = task
            todo.due = due
            todo.updated_at = now
    return RedirectResponse("/", status_code=303)

@app.get("/todos/upcoming", response_class=HTMLResponse)
def get_upcoming(request: Request):
    today = date.today()
    today_str = today.isoformat()
    upcoming = [todo for todo in todos if todo.due >= today]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "todos": upcoming,
        "today": today_str
    })
