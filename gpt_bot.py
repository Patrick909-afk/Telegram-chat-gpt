from telethon import TelegramClient, events
import requests
import asyncio
from config import OR_KEY  # Токен берётся из config.py

# Telegram API ID и HASH
api_id = 94575
api_hash = 'a3406de8d171bb422bb6ddf3bbd800e2'
client = TelegramClient('anon', api_id, api_hash)

# Модель для OpenRouter
MODEL = "deepseek/deepseek-chat-v3-0324:free"

def ask_or(prompt):
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OR_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            },
            timeout=60
        )
        if res.status_code != 200:
            return f"⚠️ Ошибка API {res.status_code}: {res.text}"
        return res.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"❌ Ошибка запроса: {e}"

@client.on(events.NewMessage)
async def handler(event):
    if not event.raw_text.startswith("/gpt"):
        return

    prompt = event.raw_text[4:].strip()
    await event.delete()

    if not prompt:
        await event.respond("⚠️ Пустой запрос.")
        return

    msg = await event.respond("⌛ Печатает")
    animating = True

    async def animate():
        dots = ["", ".", "..", "..."]
        i = 0
        while animating:
            await msg.edit(f"⌛ Печатает{dots[i % 4]}")
            i += 1
            await asyncio.sleep(0.7)

    task = asyncio.create_task(animate())
    reply = ask_or(prompt)
    animating = False
    await task

    sender = await event.get_sender()
    username = sender.username or sender.first_name or "Пользователь"

    await msg.edit(
        f"🧑‍💬 <b>Вопрос от @{username}:</b>\n{prompt}\n\n"
        f"🤖 <b>Ответ от DeepSeek V3:</b>\n\n{reply}",
        parse_mode="html"
    )

client.start()
print("✅ Бот запущен. Пиши /gpt ...")
client.run_until_disconnected()
