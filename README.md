import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from googletrans import Translator
from dotenv import load_dotenv

# .env fayldagi tokenlarni yuklash
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

# Logging
logging.basicConfig(level=logging.INFO)

# Bot va dispatcher
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode="Markdown")
)
dp = Dispatcher()

# Tarjimon
translator = Translator()

# Tanlangan matnni vaqtincha saqlash
user_texts = {}

# --- Klaviatura yaratish funksiyasi ---
def lang_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O‘zbek", callback_data="lang_uz")
    kb.button(text="🇬🇧 Ingliz", callback_data="lang_en")
    kb.button(text="🇰🇷 Koreys", callback_data="lang_ko")
    kb.button(text="🇷🇺 Rus", callback_data="lang_ru")
    kb.adjust(2)
    return kb.as_markup()

# --- /start komandasi ---
@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(
        "👋 *Salom!* Xush kelibsiz 😊\n\n"
        "🌐 Men *Tarjimon Bot*man — siz yuborgan matnni turli tillarga tarjima qilib beraman.\n\n"
        "📌 *Qanday ishlaydi?*\n"
        "1️⃣ Matn yuboring ✍️\n"
        "2️⃣ Kerakli tilni tanlang 🌍\n"
        "3️⃣ Tarjimani oling 🚀\n\n"
        "🌎 Mavjud tillar:\n"
        "🇺🇿 O‘zbek | 🇬🇧 Ingliz | 🇰🇷 Koreys | 🇷🇺 Rus\n\n"
        "⚠️ *Eslatma:* Bot hozir test rejimida ishlamoqda.\n"
        "Ba’zi hollarda xatoliklar yuz berishi mumkin.\n\n"
        "🔄 Agar muammo yuz bersa, iltimos qayta urinib ko‘ring.\n"
        "📩 Xatoliklar yoki takliflar bo‘lsa: *@dilmurodbe_05* ga yozishingiz mumkin\n\n"
        "🙏 Tushunganingiz uchun rahmat!\n\n"
        "✍️ Endi matn yuboring!"
    )
# --- Oddiy matnni qabul qilish ---
@dp.message()
async def get_text(message: Message):
    user_texts[message.from_user.id] = message.text
    await message.answer(
        f"📥 Siz yubordingiz:\n`{message.text}`\n\n"
        "🌍 Qaysi tilga tarjima qilay?",
        reply_markup=lang_keyboard()
    )

# --- Til tugmalari bosilganda ---
@dp.callback_query(F.data.startswith("lang_"))
async def translate_text(call: CallbackQuery):
    user_id = call.from_user.id
    lang = call.data.split("_")[1]   # masalan lang_en → "en"
    text = user_texts.get(user_id)

    if not text:
        await call.message.edit_text("❌ Avval matn yuboring.")
        return

    try:
        translated = translator.translate(text, dest=lang)
        await call.message.edit_text(
            f"📥 *Matn:* `{text}`\n\n"
            f"📤 *Tarjima ({lang}):* \n👉 *{translated.text}*"
        )
    except Exception:
        await call.message.edit_text("❌ Tarjima qilishda xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
