from telethon import TelegramClient, events
import requests
import asyncio

# Telegram API данные
api_id = 94575
api_hash = 'a3406de8d171bb422bb6ddf3bbd800e2'
client = TelegramClient('anon', api_id, api_hash)

# OpenRouter API
OR_KEY = "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"
MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Получить ответ от ИИ
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

# Обработчик сообщений
@client.on(events.NewMessage)
async def handler(event):
    if not event.raw_text.startswith("/gpt"):
        return

    prompt = event.raw_text[4:].strip()
    await event.delete()

    if not prompt:
        await event.respond("⚠️ Пустой запрос.")
        return

    # Сообщение-заглушка
    msg = await event.respond("⌛ Печатает")

    # Анимация ожидания (параллельно с запросом)
    animating = True

    async def animate():
        dots = ["", ".", "..", "..."]
        i = 0
        while animating:
            await msg.edit(f"⌛ Печатает{dots[i % 4]}")
            i += 1
            await asyncio.sleep(0.7)

    task = asyncio.create_task(animate())

    # Получение ответа
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