import asyncio
import json
import os
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from datetime import datetime

logging.basicConfig(level=logging.INFO)
TOKEN = '7597124882:AAGrU0WG_6LOQZr-UePPaQorugB1xmsAPOo'
ADMIN_ID = 1609956648

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

DATA_FILE = 'secret_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            if not isinstance(data.get("secrets"), list):
                data["secrets"] = []
            if not isinstance(data.get("stats"), dict):
                data["stats"] = {"sent": 0, "opened": 0}
            if not isinstance(data.get("bonus"), dict):
                data["bonus"] = {}
            if not isinstance(data.get("paid"), dict):
                data["paid"] = {}
            return data
        except Exception:
            pass
    return {"secrets": [], "stats": {"sent": 0, "opened": 0}, "bonus": {}, "paid": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("👋 Привет! Этот бот позволяет отправлять приватные анонимные секреты и немного веселиться 😉\nНапиши /help чтобы узнать всё!")

@dp.message_handler(commands=['help'])
async def help_cmd(message: types.Message):
    await message.answer(
        "🤖 <b>Что умеет бот:</b>\n"
        "• Отправка приватных секретов (@бот username текст)\n"
        "• Ежедневный бонус просмотров\n"
        "• Рандом dick / gay / pidor\n\n"
        "<b>Команды:</b>\n"
        "/list – непрочитанные секреты\n"
        "/stats – статистика\n"
        "/my – мои просмотры\n"
        "/bonus – получить бонус\n"
        "/buy – как купить доступ\n"
        "/help – это сообщение"
    )

@dp.message_handler(commands=['buy'])
async def buy_cmd(message: types.Message):
    await message.answer("💰 Чтобы купить доступ к просмотру чужих секретов, пиши админу: @gde_patrick")

@dp.message_handler(commands=['bonus'])
async def bonus_cmd(message: types.Message):
    data = load_data()
    user_id = str(message.from_user.id)
    today = datetime.now().strftime("%Y-%m-%d")
    if data["bonus"].get(user_id) == today:
        return await message.answer("✅ Ты уже получал бонус сегодня!")
    data["bonus"][user_id] = today
    data["paid"][user_id] = data["paid"].get(user_id, 0) + 1
    save_data(data)
    await message.answer("🎉 Поздравляю! Ты получил 1 бесплатный просмотр.\nВозвращайся завтра за новым бонусом!")

@dp.message_handler(commands=['my'])
async def my_cmd(message: types.Message):
    data = load_data()
    count = data["paid"].get(str(message.from_user.id), 0)
    await message.answer(f"🔑 У тебя {count} платных просмотров.")

@dp.message_handler(commands=['add'])
async def add_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) != 3:
        return await message.reply("⚠ Используй: /add user_id количество")
    user_id, amount = parts[1], parts[2]
    if not amount.isdigit():
        return await message.reply("❌ Неверное количество.")
    data = load_data()
    data["paid"][user_id] = data["paid"].get(user_id, 0) + int(amount)
    save_data(data)
    await message.reply(f"✅ Выдано пользователю {user_id}: {amount} просмотров.")

@dp.message_handler(commands=['list'])
async def list_cmd(message: types.Message):
    data = load_data()
    my_username = (message.from_user.username or '').lower()
    my_id = message.from_user.id
    my_secrets = [
        s for s in data["secrets"]
        if not s["read"] and (
            (my_username and s["to"] == my_username) or s.get("to_id") == my_id
        )
    ]
    if not my_secrets:
        return await message.answer("✅ У тебя нет непрочитанных секретов.")
    text = "\n".join([f"🔑 ID: {s['id']} | От: @{s['from']}" for s in my_secrets])
    await message.answer(f"📋 Твои непрочитанные секреты:\n{text}")

@dp.message_handler(commands=['stats'])
async def stats_cmd(message: types.Message):
    data = load_data()
    await message.answer(f"📊 Статистика:\n• Отправлено: {data['stats']['sent']}\n• Прочитано: {data['stats']['opened']}")

@dp.message_handler(commands=['del'])
async def del_cmd(message: types.Message):
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("⚠ Используй: /del ID")
    secret_id = parts[1]
    data = load_data()
    before = len(data["secrets"])
    my_username = (message.from_user.username or '').lower()
    my_id = message.from_user.id
    data["secrets"] = [
        s for s in data["secrets"]
        if not (s["id"] == secret_id and (
            (my_username and s["to"] == my_username) or s.get("to_id") == my_id
        ))
    ]
    after = len(data["secrets"])
    save_data(data)
    if before == after:
        await message.answer("❌ Не найдено или не твоё сообщение.")
    else:
        await message.answer(f"🗑️ Сообщение с ID {secret_id} удалено!")

@dp.inline_handler()
async def inline_secret(query: types.InlineQuery):
    text = query.query.strip()
    args = text.split(maxsplit=1)
    data = load_data()

    # dick
    if text.lower() == "dick":
        size = round(random.uniform(-0.55, 204.55), 2)
        desc = random.choice(["🔥 У тебя вагина!", "😂 Да у тебя как спичка!", "💪 Ого, неплохо!", "🤣 Легендарный!", "🤡 Что это?"])
        await query.answer([
            InlineQueryResultArticle(
                id='dick',
                title=f"📏🍌 {size} см",
                description=desc,
                input_message_content=InputTextMessageContent(f"📏🍌 Мой размер члена: {size} см - {desc}"),
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("😎 Узнать свой!", switch_inline_query_current_chat="dick"))
            )
        ], cache_time=1)
        return

    # gay
    if text.lower() == "gay":
        percent = round(random.uniform(0, 100), 2)
        desc = random.choice(["🏳️‍🌈 Ты очень гей!", "😏 Есть немного", "😂 Почти нет!", "🔥 Максимум!", "🤣 Легенда!"])
        await query.answer([
            InlineQueryResultArticle(
                id='gay',
                title=f"🌈 {percent}%",
                description=desc,
                input_message_content=InputTextMessageContent(f"🌈 Я гей на {percent}% - {desc}"),
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🌈 Узнать свой!", switch_inline_query_current_chat="gay"))
            )
        ], cache_time=1)
        return

    # pidor
    if text.lower() == "pidor":
        percent = round(random.uniform(0, 100), 2)
        desc = random.choice(["😂 Пидор конкретный!", "😏 Есть чуть-чуть", "🤣 Почти не пидор!", "🔥 Ну ты даёшь!", "🤡 Легендарный!"])
        await query.answer([
            InlineQueryResultArticle(
                id='pidor',
                title=f"🤡 {percent}%",
                description=desc,
                input_message_content=InputTextMessageContent(f"🤡 Я пидор на {percent}% - {desc}"),
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🤡 Узнать свой!", switch_inline_query_current_chat="pidor"))
            )
        ], cache_time=1)
        return

    if len(args) < 2:
        return await query.answer([
            InlineQueryResultArticle(
                id='help',
                title='❓ Как отправить секрет',
                description='Формат: @username текст_секрета',
                input_message_content=InputTextMessageContent(
                    "ℹ️ Возможности:\n"
                    "• dick / gay / pidor – приколы\n"
                    "• @username текст – секрет\n"
                    "• /list, /stats, /my, /bonus, /buy, /help"
                )
            )
        ], cache_time=1)

    username, secret_text = args
    if not username.startswith('@'):
        username = '@' + username
    secret_id = str(len(data["secrets"]) + 1)
    data["secrets"].append({
        "id": secret_id,
        "to": username[1:].lower(),
        "to_id": None,
        "text": secret_text,
        "from": query.from_user.username or str(query.from_user.id),
        "read": False
    })
    data["stats"]["sent"] += 1
    save_data(data)
    await query.answer([
        InlineQueryResultArticle(
            id=secret_id,
            title=f"🔒 Секрет для {username}",
            description=f"От: @{query.from_user.username or query.from_user.id}",
            input_message_content=InputTextMessageContent(f"👀 Секретное сообщение для {username}!"),
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔓 Прочитать", callback_data=f"open_{secret_id}")
            )
        )
    ], cache_time=1)

@dp.callback_query_handler(lambda c: c.data.startswith("open_"))
async def open_secret(call: types.CallbackQuery):
    secret_id = call.data.split('_')[1]
    data = load_data()
    secret = next((s for s in data["secrets"] if s["id"] == secret_id), None)
    if not secret:
        return await call.answer("❌ Сообщение не найдено!", show_alert=True)
    user_id = str(call.from_user.id)
    my_username = (call.from_user.username or '').lower()
    paid = data["paid"].get(user_id, 0)
    user_ok = False
    if (my_username and my_username == secret["to"]) or (secret.get("to_id") and call.from_user.id == secret["to_id"]):
        user_ok = True
    elif paid > 0:
        data["paid"][user_id] -= 1
        user_ok = True
    if not secret.get("to_id"):
        secret["to_id"] = call.from_user.id
    if not user_ok:
        return await call.answer("🚫 Это не для тебя! Хочешь доступ? Пиши @gde_patrick", show_alert=True)
    secret["read"] = True
    data["stats"]["opened"] += 1
    save_data(data)
    await call.answer(f"📨 От @{secret['from']}:\n{secret['text']}", show_alert=True)

if __name__ == '__main__':
    print("🤖 Бот запущен!")
    asyncio.run(dp.start_polling())
