import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# --- .env yuklash ---
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


user_texts = {}

# --- Klaviatura ---
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

# --- Foydalanuvchi matn yuborsa ---
@dp.message()
async def get_text(message: Message):
    user_texts[message.from_user.id] = message.text.strip()
    await message.answer(
        f"📥 Siz yubordingiz:\n`{message.text}`\n\n"
        "🌍 Qaysi tilga tarjima qilay?",
        reply_markup=lang_keyboard()
    )

# --- Tarjima ---
@dp.callback_query(F.data.startswith("lang_"))
async def translate_text(call: CallbackQuery):
    user_id = call.from_user.id
    lang = call.data.split("_")[1]
    text = user_texts.get(user_id)

    if not text:
        await call.message.edit_text("❌ Avval matn yuboring.")
        return

    try:
        translated = GoogleTranslator(source='auto', target=lang).translate(text)
        await call.message.edit_text(
            f"📥 *Matn:* `{text}`\n\n"
            f"📤 *Tarjima ({lang}):*\n👉 *{translated}*"
        )
    except Exception as e:
        logging.error(f"Tarjima xatolik: {e}")
        await call.message.edit_text("❌ Tarjima qilishda xatolik yuz berdi.")

# --- Webhook server ---
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

def main():
    app = web.Application()
    # Dispatcher uchun handler
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == "__main__":
    main()
