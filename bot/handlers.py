from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json
import aiohttp
from config import APP_URL

router = Router()

class BotStates(StatesGroup):
    waiting_task = State()
    waiting_user_name = State()
    waiting_user_email = State()

# Клавиатура меню
def get_main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мои TODO", callback_data="my_todos")],
        [InlineKeyboardButton(text="➕ Новый TODO", callback_data="add_todo")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="users")],
        [InlineKeyboardButton(text="🔄 Health", callback_data="health")],
        [InlineKeyboardButton(text="⚙️ Управление", callback_data="manage")]
    ])
    return kb

@router.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(
        "🚀 <b>TODO Bot Frontend</b>\n\n"
        "Ваш FastAPI TODO API доступен через Telegram!\n"
        f"🌐 API: <code>{APP_URL}</code>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "health")
async def health_cb(callback: CallbackQuery):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{APP_URL}/health") as resp:
            data = await resp.json()
    status = "🟢 OK" if data.get("status") == "healthy" else "🔴 ERROR"
    await callback.message.edit_text(
        f"🏥 Health Check\n\n<code>{json.dumps(data, indent=2, ensure_ascii=False)}</code>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "stats")
async def stats_cb(callback: CallbackQuery):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{APP_URL}/stats") as resp:
            data = await resp.json()
    await callback.message.edit_text(
        f"📊 Общая статистика\n\n"
        f"Всего: {data.get('total', 0)} 📝\n"
        f"Выполнено: {data.get('completed', 0)} ✅\n"
        f"Осталось: {data.get('pending', 0)} ⏳",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "users")
async def users_cb(callback: CallbackQuery):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{APP_URL}/users") as resp:
            users = await resp.json()
    text = "👥 Пользователи:\n\n" + "\n".join(
        [f"• {u['name']} ({u['email']})" for u in users[:10]]
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu())
    await callback.answer()

@router.callback_query(F.data == "my_todos")
async def my_todos_cb(callback: CallbackQuery, state: FSMContext):
    # Для простоты показываем все TODO (можно добавить user_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{APP_URL}/todos") as resp:
            todos = await resp.json()
    
    if not todos:
        await callback.message.edit_text("📭 TODO пусто", reply_markup=get_main_menu())
        return
    
    text = "📋 TODO:\n\n"
    for todo in todos[:10]:
        status = "✅" if todo['completed'] else "⏳"
        text += f"{status} <code>{todo['task']}</code>\n"
    
    await callback.message.edit_text(text, reply_markup=get_main_menu(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "add_todo")
async def add_todo_cb(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "➕ Введите задачу:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
    )
    await state.set_state(BotStates.waiting_task)
    await callback.answer()

@router.message(BotStates.waiting_task)
async def process_task(msg: Message, state: FSMContext):
    task = msg.text.strip()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{APP_URL}/todos", json={
            "user_id": 1,      # ← ИСПРАВЛЕНО!
            "task": task,
            "completed": False
        }) as resp:
            result = await resp.json()
    
    await msg.answer("✅ Задача добавлена!", reply_markup=get_main_menu())
    await state.clear()


@router.callback_query(F.data == "cancel")
async def cancel_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Отменено", reply_markup=get_main_menu())
    await callback.answer()

@router.callback_query(F.data == "manage")
async def manage_cb(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ <b>Управление задачами:</b>\n\n"
        "• <code>/complete ID</code> - завершить задачу\n"
        "• <code>/delete ID</code> - удалить задачу\n\n"
        "<i>ID смотрите в списке TODO</i>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@router.message(Command("complete"))
async def cmd_complete(msg: Message):
    try:
        todo_id = int(msg.text.split()[1])
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{APP_URL}/todos/{todo_id}", json={
                "task": "Завершено", "completed": True
            }) as resp:
                result = await resp.json()
        await msg.answer(f"✅ Задача {todo_id} завершена!")
    except:
        await msg.answer("❌ Используйте: /complete 1")

@router.message(Command("delete"))
async def cmd_delete(msg: Message):
    try:
        todo_id = int(msg.text.split()[1])
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{APP_URL}/todos/{todo_id}") as resp:
                result = await resp.json()
        await msg.answer(f"🗑 Задача {todo_id} удалена!")
    except:
        await msg.answer("❌ Используйте: /delete 1")
