import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from googletrans import Translator
from dotenv import load_dotenv
from aiohttp import web

# --- .env dan yuklash ---
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # masalan: https://your-app.onrender.com/webhook
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8080))

if not API_TOKEN:
    raise ValueError("❌ BOT_TOKEN .env faylida topilmadi!")

# Logging
logging.basicConfig(level=logging.INFO)

# Bot va dispatcher
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode="Markdown")
)
dp = Dispatcher()

# Google Translator
translator = Translator()
user_texts = {}

# --- Klaviatura yaratish ---
def lang_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O‘zbek", callback_data="lang_uz")
    kb.button(text="🇬🇧 Ingliz", callback_data="lang_en")
    kb.button(text="🇰🇷 Koreys", callback_data="lang_ko")
    kb.button(text="🇷🇺 Rus", callback_data="lang_ru")
    kb.adjust(2)
    return kb.as_markup()

# --- /start ---
@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(
        "👋 *Salom!* Men *Tarjimon Bot*man 🌐\n\n"
        "✍️ Matn yuboring, keyin tarjima qilmoqchi bo‘lgan tilni tanlang."
    )

# --- Foydalanuvchi matn yuborganda ---
@dp.message()
async def get_text(message: Message):
    user_texts[message.from_user.id] = message.text.strip()
    await message.answer(
        f"📥 Siz yubordingiz:\n`{message.text}`\n\n"
        "🌍 Qaysi tilga tarjima qilay?",
        reply_markup=lang_keyboard()
    )

# --- Tarjima qilish ---
@dp.callback_query(F.data.startswith("lang_"))
async def translate_text(call: CallbackQuery):
    user_id = call.from_user.id
    lang = call.data.split("_")[1]
    text = user_texts.get(user_id)

    if not text:
        await call.message.edit_text("❌ Avval matn yuboring.")
        return

    try:
        translated = translator.translate(text, dest=lang)
        await call.message.edit_text(
            f"📥 *Matn:* `{text}`\n\n"
            f"📤 *Tarjima ({lang}):*\n👉 *{translated.text}*"
        )
    except Exception as e:
        logging.error(f"Tarjima xatolik: {e}")
        await call.message.edit_text("❌ Tarjima qilishda xatolik yuz berdi.")

# --- Webhook server ---
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    logging.warning("Bot o‘chmoqda...")
    await bot.delete_webhook()
    await bot.session.close()

async def main():
    app = web.Application()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    app.router.add_post("/webhook", dp.webhook_handler)
    return app

if __name__ == "__main__":
    web.run_app(main(), host=WEBAPP_HOST, port=WEBAPP_PORT)
