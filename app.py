from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Optional
import time
from psycopg2 import OperationalError

app = FastAPI(title="TODO API", version="1.0.0")

# ===== Models =====
class UserCreate(BaseModel):
    name: str
    email: EmailStr

class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: str

class TodoCreate(BaseModel):
    user_id: int
    task: str
    completed: Optional[bool] = False

class TodoUpdate(BaseModel):
    task: str
    completed: bool

class Todo(BaseModel):
    id: int
    user_id: int
    task: str
    completed: bool
    created_at: str

# ===== Database =====
def get_db_connection_with_retry(max_retries=10, delay=2):
    """Подключение к БД с повторами"""
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host='postgres',
                database='myapp',
                user='admin',
                password='admin',
                port=5432
            )
            return conn
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"✗ Попытка {attempt + 1}/{max_retries}: {e}")
                time.sleep(delay)
            else:
                raise

def get_db_connection():
    return get_db_connection_with_retry()

def init_schema():
    """Инициализация БД из schema.sql"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        with open('/app/schema.sql', 'r') as f:
            schema = f.read()
        
        cursor.execute(schema)
        conn.commit()
        cursor.close()
        conn.close()
        print("✓ База данных инициализирована")
    except Exception as e:
        print(f"✗ Ошибка инициализации БД: {e}")

init_schema()

# ===== Main Endpoints =====
@app.get("/")
def read_root():
    """Главная страница с информацией об API"""
    return {
        "message": "FastAPI TODO API с управлением пользователями!",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "users": {
                "GET /users": "Получить всех пользователей",
                "POST /users": "Создать нового пользователя",
                "GET /users/{id}": "Получить пользователя по ID",
            },
            "todos": {
                "GET /todos": "Получить все задачи",
                "POST /todos": "Создать новую задачу",
                "GET /todos/{id}": "Получить задачу по ID",
                "PUT /todos/{id}": "Обновить задачу",
                "DELETE /todos/{id}": "Удалить задачу",
            },
            "stats": {
                "GET /stats": "Статистика по задачам",
                "GET /stats/users": "Статистика по пользователям",
            }
        }
    }

@app.get("/health")
def health_check():
    """Проверка здоровья приложения"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# ===== User Endpoints =====
@app.get("/users", response_model=List[User])
def get_users():
    """Получить всех пользователей"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT id, name, email, created_at::text FROM users ORDER BY id')
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [dict(user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

@app.post("/users", response_model=dict, status_code=201)
def create_user(user: UserCreate):
    """Создать нового пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id',
            (user.name, user.email)
        )
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Пользователь создан",
            "id": user_id,
            "name": user.name,
            "email": user.email
        }
    except psycopg2.IntegrityError:
        raise HTTPException(status_code=400, detail="Email уже существует")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    """Получить пользователя по ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT id, name, email, created_at::text FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return dict(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

# ===== Todo Endpoints =====
@app.get("/todos", response_model=List[Todo])
def get_todos():
    """Получить все задачи"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, user_id, task, completed, created_at::text 
            FROM todos 
            ORDER BY created_at DESC
        ''')
        todos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [dict(todo) for todo in todos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

@app.post("/todos", response_model=dict, status_code=201)
def create_todo(todo: TodoCreate):
    """Создать новую задачу"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Проверка существования пользователя
        cursor.execute('SELECT id FROM users WHERE id = %s', (todo.user_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        cursor.execute(
            'INSERT INTO todos (user_id, task, completed, created_at) VALUES (%s, %s, %s, %s) RETURNING id',
            (todo.user_id, todo.task, todo.completed, datetime.now())
        )
        
        todo_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Задача добавлена",
            "id": todo_id,
            "user_id": todo.user_id,
            "task": todo.task
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    """Получить задачу по ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, user_id, task, completed, created_at::text 
            FROM todos 
            WHERE id = %s
        ''', (todo_id,))
        todo = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not todo:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        return dict(todo)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

@app.put("/todos/{todo_id}", response_model=dict)
def update_todo(todo_id: int, todo: TodoUpdate):
    """Обновить задачу"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM todos WHERE id = %s', (todo_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        cursor.execute(
            'UPDATE todos SET task = %s, completed = %s WHERE id = %s',
            (todo.task, todo.completed, todo_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Задача обновлена",
            "id": todo_id,
            "task": todo.task,
            "completed": todo.completed
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    """Удалить задачу"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT task FROM todos WHERE id = %s', (todo_id,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        task_name = result[0]
        
        cursor.execute('DELETE FROM todos WHERE id = %s', (todo_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Задача удалена",
            "id": todo_id,
            "task": task_name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

@app.get("/todos/user/{user_id}")
def get_user_todos(user_id: int):
    """Получить все задачи пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Проверка существования пользователя
        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        cursor.execute('''
            SELECT id, user_id, task, completed, created_at::text 
            FROM todos 
            WHERE user_id = %s
            ORDER BY created_at DESC
        ''', (user_id,))
        todos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [dict(todo) for todo in todos]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

# ===== Stats Endpoints =====
@app.get("/stats")
def get_stats():
    """Статистика по задачам"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN completed = true THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN completed = false THEN 1 ELSE 0 END) as pending
            FROM todos
        ''')
        
        stats = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return dict(stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

@app.get("/stats/users")
def get_users_stats():
    """Статистика по пользователям и их задачам"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT 
                u.id,
                u.name,
                u.email,
                COUNT(t.id) as total_todos,
                SUM(CASE WHEN t.completed = true THEN 1 ELSE 0 END) as completed_todos,
                SUM(CASE WHEN t.completed = false THEN 1 ELSE 0 END) as pending_todos
            FROM users u
            LEFT JOIN todos t ON u.id = t.user_id
            GROUP BY u.id, u.name, u.email
            ORDER BY u.id
        ''')
        
        stats = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(stat) for stat in stats]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
