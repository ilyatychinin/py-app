from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('/app/database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация БД при первом запуске
def init_db():
    if not os.path.exists('/app/database.db'):
        conn = get_db_connection()
        conn.execute('CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                    'task TEXT NOT NULL, completed BOOLEAN NOT NULL, created_at TEXT)')
        conn.commit()
        conn.close()
        print("База данных создана")

# Вызываем инициализацию
init_db()

@app.route('/')
def hello():
    return jsonify({"message": "Docker TODO API работает!", "endpoints": ["/todos", "/todos/<id>"]})

@app.route('/todos', methods=['GET', 'POST'])
def todos():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.get_json()
        conn.execute('INSERT INTO todos (task, completed, created_at) VALUES (?, ?, ?)',
                    (data['task'], False, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return jsonify({"message": "Задача добавлена"}), 201
    
    todos = conn.execute('SELECT * FROM todos ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(todo) for todo in todos])

@app.route('/todos/<int:todo_id>', methods=['GET', 'PUT', 'DELETE'])
def todo(todo_id):
    conn = get_db_connection()
    
    todo = conn.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    if todo is None:
        conn.close()
        return jsonify({"error": "Задача не найдена"}), 404
    
    if request.method == 'GET':
        conn.close()
        return jsonify(dict(todo))
    
    if request.method == 'PUT':
        data = request.get_json()
        conn.execute('UPDATE todos SET task = ?, completed = ? WHERE id = ?',
                    (data['task'], data['completed'], todo_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Задача обновлена"})
    
    if request.method == 'DELETE':
        conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Задача удалена"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False для продакшена
