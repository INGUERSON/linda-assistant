import json
import os
from datetime import datetime

DATA_FILE = "linda_data.json"

def _load() -> dict:
    """Carrega todos os dados salvos."""
    if not os.path.exists(DATA_FILE):
        return {"tasks": [], "projects": [], "schedule": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data: dict):
    """Salva todos os dados."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── TAREFAS ──────────────────────────────────────────────────────────────────

def add_task(title: str, priority: str = "normal", date: str = None) -> dict:
    data = _load()
    task = {
        "id": len(data["tasks"]) + 1,
        "title": title,
        "priority": priority,
        "done": False,
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat()
    }
    data["tasks"].append(task)
    _save(data)
    return task

def list_tasks(date: str = None, show_done: bool = False) -> list:
    data = _load()
    target = date or datetime.now().strftime("%Y-%m-%d")
    tasks = [t for t in data["tasks"] if t["date"] == target]
    if not show_done:
        tasks = [t for t in tasks if not t["done"]]
    return tasks

def complete_task(task_id: int) -> bool:
    data = _load()
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["done"] = True
            task["completed_at"] = datetime.now().isoformat()
            _save(data)
            return True
    return False

def delete_task(task_id: int) -> bool:
    data = _load()
    before = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    _save(data)
    return len(data["tasks"]) < before

# ─── PROJETOS ─────────────────────────────────────────────────────────────────

def add_project(name: str, description: str = "", deadline: str = None) -> dict:
    data = _load()
    project = {
        "id": len(data["projects"]) + 1,
        "name": name,
        "description": description,
        "deadline": deadline,
        "status": "em andamento",
        "steps": [],
        "created_at": datetime.now().isoformat()
    }
    data["projects"].append(project)
    _save(data)
    return project

def add_step(project_id: int, step_title: str) -> bool:
    data = _load()
    for proj in data["projects"]:
        if proj["id"] == project_id:
            proj["steps"].append({
                "id": len(proj["steps"]) + 1,
                "title": step_title,
                "done": False
            })
            _save(data)
            return True
    return False

def complete_step(project_id: int, step_id: int) -> bool:
    data = _load()
    for proj in data["projects"]:
        if proj["id"] == project_id:
            for step in proj["steps"]:
                if step["id"] == step_id:
                    step["done"] = True
                    _save(data)
                    return True
    return False

def list_projects(active_only: bool = True) -> list:
    data = _load()
    if active_only:
        return [p for p in data["projects"] if p["status"] != "concluído"]
    return data["projects"]

def finish_project(project_id: int) -> bool:
    data = _load()
    for proj in data["projects"]:
        if proj["id"] == project_id:
            proj["status"] = "concluído"
            proj["finished_at"] = datetime.now().isoformat()
            _save(data)
            return True
    return False

# ─── CRONOGRAMA ───────────────────────────────────────────────────────────────

def add_schedule_entry(date: str, time: str, event: str) -> dict:
    data = _load()
    if date not in data["schedule"]:
        data["schedule"][date] = []
    entry = {
        "id": sum(len(v) for v in data["schedule"].values()) + 1,
        "time": time,
        "event": event
    }
    data["schedule"][date].append(entry)
    data["schedule"][date].sort(key=lambda x: x["time"])
    _save(data)
    return entry

def get_schedule(date: str = None) -> list:
    data = _load()
    target = date or datetime.now().strftime("%Y-%m-%d")
    return data["schedule"].get(target, [])

def get_summary() -> dict:
    """Resumo geral para o chefe."""
    data = _load()
    today = datetime.now().strftime("%Y-%m-%d")
    pending_today = [t for t in data["tasks"] if t["date"] == today and not t["done"]]
    done_today = [t for t in data["tasks"] if t["date"] == today and t["done"]]
    active_projects = [p for p in data["projects"] if p["status"] != "concluído"]
    agenda_today = data["schedule"].get(today, [])
    return {
        "pending_tasks": len(pending_today),
        "done_tasks": len(done_today),
        "active_projects": len(active_projects),
        "agenda_count": len(agenda_today),
        "tasks": pending_today,
        "agenda": agenda_today,
        "projects": active_projects
    }
