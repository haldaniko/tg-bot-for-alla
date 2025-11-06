from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
import asyncio

from config import TOKEN, GROUP_ID, GROUP_LINK, MANUAL_FILE_ID, MANUAL_LOCAL_PATH
from scheduler import schedule_messages
from database import init_db, add_user, update_subscription

bot = Bot(token=TOKEN)
dp = Dispatcher()

KEYWORDS = ["/start"]

WELCOME_MESSAGE = f"""🔥 Дякуємо що звернулись у ЦЕНТР ПІДТРИМКИ БІЗНЕСУ українців в Болгарії 🇺🇦🇧🇬.

👉 Приєднайтесь до [нашої спільноти]({GROUP_LINK}).

Після вступу натисніть ✅ і ми надішлемо посібник.
"""

REMIND_MESSAGE = f"""🤔 Для отримання посібника потрібно приєднатись до нашої спільноти.
👉 [Підписатись тут]({GROUP_LINK})
"""

CONFIRM_MESSAGE = """Підписка підтверджена! ✅

У нашій спільноті Ви зможете:
🤝Знайти нові контакти.
👍Безкоштовно прорекламувати свій бізнес.
🫶Отримати безкоштовну консультацію.

Дякуємо що Ви з нами 💛💙

Надсилаємо Ваш посібник нижче ⬇️
"""

join_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Підтвердити підписку", callback_data="check_join")]
])


async def safe_edit_text(message: types.Message, text: str, *, parse_mode: str | None = None,
                         reply_markup: InlineKeyboardMarkup | None = None):
    """Safely edit message text: ignore 'message is not modified' error on duplicate edits."""
    try:
        if (message.text or "") == text and (reply_markup is None or message.reply_markup == reply_markup):
            return
        await message.edit_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return
        raise


@dp.message(CommandStart())
async def handle_keyword(message: types.Message):
    await add_user(message.from_user.id)
    await message.answer(WELCOME_MESSAGE, parse_mode="Markdown", reply_markup=join_btn)


@dp.callback_query(lambda c: c.data == "check_join")
async def confirm_join(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    try:
        chat_member = await bot.get_chat_member(GROUP_ID, user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            await update_subscription(user_id, True)
            await safe_edit_text(callback.message, CONFIRM_MESSAGE, parse_mode="Markdown")
            await callback.answer("✅ Підписка підтверджена", show_alert=False, cache_time=3)

            if MANUAL_FILE_ID:
                await bot.send_document(user_id, document=MANUAL_FILE_ID, caption="📘 Бізнес-посібник")
            else:
                doc = FSInputFile(MANUAL_LOCAL_PATH)
                sent = await bot.send_document(user_id, document=doc, caption="📘 Бізнес-посібник")
                print("MANUAL_FILE_ID =", sent.document.file_id)
        else:
            await safe_edit_text(callback.message, REMIND_MESSAGE, parse_mode="Markdown", reply_markup=join_btn)
            await callback.answer("👆 Спочатку приєднайтесь до спільноти", show_alert=False, cache_time=3)
    except Exception as e:
        print(f"Помилка перевірки: {e}")
        await safe_edit_text(callback.message, REMIND_MESSAGE, parse_mode="Markdown", reply_markup=join_btn)
        await callback.answer("Спробуйте ще раз пізніше", show_alert=False, cache_time=3)


async def main():
    await init_db()
    asyncio.create_task(schedule_messages(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
