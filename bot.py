import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from gigachat import GigaChat


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
BOT_TOKEN = "8749792054:AAGUl5Oc0CsiHCTuQ4LA91tqZMDNXj0Kd1E"
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Хранилище истории сообщений
user_history = {}

# Инициализация Гигачата
GIGA_TOKEN = "MDE5YmYwOGEtNTgzYy03NGEyLWFmN2MtYmNmYzc1YTNjOGJjOmQ4YzJjN2ZjLWZmMmEtNGJiNC1iZmI0LTRiYmY2NzRlN2ZkMQ=="
giga = GigaChat(
    credentials=GIGA_TOKEN,
    verify_ssl_certs=False
)

# /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "👋 <b>Привет!</b>\n\n"
        "Я — <b>Гигачат 🤖</b>\n"
        "Задай мне любой вопрос, и я постараюсь помочь 💡\n\n"
        "📖 Напиши /help чтобы увидеть список команд\n"
    )
    await message.answer(welcome_text)


#  помощь
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📖 <b>Доступные команды:</b>\n\n"
        "🚀 /start — запуск бота\n"
        "❓ /help — помощь\n"
        "📜 /history — последние сообщения\n\n"
        "Просто напиши любой текст — я отвечу 😉"
    )
    await message.answer(help_text)


#  история
@dp.message(Command("history"))
async def cmd_history(message: Message):
    user_id = message.from_user.id
    history = user_history.get(user_id, [])

    if not history:
        await message.answer("📭 История пока пуста")
        return

    text = "📜 <b>Твоя история сообщений:</b>\n\n"
    text += "\n".join(history[-10:])

    await message.answer(text)


#  обработка текста
@dp.message(F.text)
async def request_gigachat(message: Message):
    query = message.text.strip()
    user_id = message.from_user.id

    if user_id not in user_history:
        user_history[user_id] = []

    user_history[user_id].append(query)

    # Ограничение истории
    user_history[user_id] = user_history[user_id][-50:]

    status_msg = await message.answer("🔍 Думаю над ответом...")

    try:
        response = giga.chat(query)

        await status_msg.delete()

        answer = response.choices[0].message.content

        # Сохраняем ответ
        user_history[user_id].append(f"🤖 {answer}")

        await message.answer(answer, disable_web_page_preview=True)

    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        await status_msg.edit_text("❌ Произошла ошибка. Попробуй позже.")


async def main():
    logger.info("Запуск бота...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
