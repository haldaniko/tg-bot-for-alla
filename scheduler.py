import asyncio
from datetime import datetime, timezone, timedelta
from database import get_all_users, mark_reminder_sent
from aiogram.types import LinkPreviewOptions


async def send_message(bot, user_id, text):
    try:
        await bot.send_message(
            user_id,
            text,
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    except:
        pass


MSG_1 = """
Привіт! 😻

Це ЦЕНТР ПІДТРИМКИ БІЗНЕСУ українців в Болгарії 🇧🇬 🇺🇦

Чи знайшов ти усі відповіді про бізнес в Болгарії у нашому посібнику?

Якщо ні, то пиши нашому менеджеру: @Manager_Alla_Mi

<a href=\"https://www.instagram.com/biznesvsofij\">Instagram</a> | <a href=\"https://www.facebook.com/groups/576711572108058/\">Facebook</a> | <a href=\"https://www.linkedin.com/company/107202554/\">LinkedIn</a>
"""

MSG_2 = """
Нагадуємо! 🔥

ЦЕНТР ПІДТРИМКИ БІЗНЕСУ українців в Болгарії 🇧🇬 🇺🇦 має активні спільноти в <a href=\"https://www.instagram.com/biznesvsofij\">Instagram</a>, <a href=\"https://www.facebook.com/groups/576711572108058/\">Facebook</a> та <a href=\"https://www.linkedin.com/company/107202554/\">LinkedIn</a> де ти зможеш прорекламувати свій бізнес, знайти нові бізнесові знайомства, приєднатись до нетворкінгу.

Підписуйся, щоб бути в Курсі усіх бізнесових новин у Болгарії!
<a href=\"https://www.instagram.com/biznesvsofij\">Instagram</a> | <a href=\"https://www.facebook.com/groups/576711572108058/\">Facebook</a> | <a href=\"https://www.linkedin.com/company/107202554/\">LinkedIn</a>
"""

MSG_3 = """
Нагадуємо! 🔥

Що до кінця року у ЦЕНТРУ ПІДТРИМКИ БІЗНЕСУ українців в Болгарії 🇺🇦 🇧🇬 діє неймовірна ціна на відкриття ООД або ДПК усього 250€!

Замовити послугу можна у менеджера: @Manager_Alla_Mi

<a href=\"https://www.instagram.com/biznesvsofij\">Instagram</a> | <a href=\"https://www.facebook.com/groups/576711572108058/\">Facebook</a> | <a href=\"https://www.linkedin.com/company/107202554/\">LinkedIn</a>
"""

MSG_4 = """
Привіт! 😻

Це ЦЕНТР ПІДТРИМКИ БІЗНЕСУ українців в Болгарії 🇧🇬🇺🇦 

У тебе є неймовірна можливіть записатись на безкоштовну консультацію з питань бізнесу в Болгарії 🔥

Швиденько пиши нашому менеджеру: @Manager_Alla_Mi

<a href=\"https://www.instagram.com/biznesvsofij\">Instagram</a> | <a href=\"https://www.facebook.com/groups/576711572108058/\">Facebook</a> | <a href=\"https://www.linkedin.com/company/107202554/\">LinkedIn</a>
"""


def _parse_joined_at(value: str) -> datetime:
    # SQLite returns 'YYYY-MM-DD HH:MM:SS'
    try:
        dt = datetime.fromisoformat(value)
    except Exception:
        # Fallback parsing
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    # Assume stored in local time; normalize to UTC-naive for comparison consistency
    return dt.replace(tzinfo=None)


async def schedule_messages(bot):
    CHECK_INTERVAL = 10  # check every 10 seconds to catch 1-minute window
    while True:
        try:
            users = await get_all_users()
            now = datetime.utcnow()
            for row in users:
                user_id = row["user_id"] if isinstance(row, dict) else row[0]
                joined_at = row["joined_at"] if isinstance(row, dict) else row[2]
                r1 = row["reminder1_sent"] if isinstance(row, dict) else row[3]
                r2 = row["reminder2_sent"] if isinstance(row, dict) else row[4]
                r3 = row["reminder3_sent"] if isinstance(row, dict) else row[5]
                r4 = row["reminder4_sent"] if isinstance(row, dict) else row[6]

                try:
                    base = _parse_joined_at(joined_at) if isinstance(joined_at, str) else joined_at
                except Exception:
                    continue

                # Due times (test timings): +30s, +40s, +50s, +70s from joined_at
                if not r1 and now >= base + timedelta(seconds=30):
                    await send_message(bot, user_id, MSG_1)
                    await mark_reminder_sent(user_id, 1)
                    continue  # one step per pass per user

                if r1 and not r2 and now >= base + timedelta(seconds=40):
                    await send_message(bot, user_id, MSG_2)
                    await mark_reminder_sent(user_id, 2)
                    continue

                if r2 and not r3 and now >= base + timedelta(seconds=50):
                    await send_message(bot, user_id, MSG_3)
                    await mark_reminder_sent(user_id, 3)
                    continue

                if r3 and not r4 and now >= base + timedelta(seconds=70):
                    await send_message(bot, user_id, MSG_4)
                    await mark_reminder_sent(user_id, 4)
                    continue
        except Exception:
            # silent cycle; optionally log
            pass
        await asyncio.sleep(CHECK_INTERVAL)
