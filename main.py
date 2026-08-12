import os
import nest_asyncio
nest_asyncio.apply()
import logging
from telegram.ext import (
    Application, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    filters
)

from database import init_db
from user import register_user_handlers
from admin import register_admin_handlers

# —— SOZLAMALAR ——
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6832985197  # O'zingizning ID ingiz

logging.basicConfig(level=logging.INFO)

def main():
    import asyncio
    asyncio.get_event_loop().run_until_complete(init_db())

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN topilmadi! Render Environment Variables qismini tekshiring.")

    app = Application.builder().token(BOT_TOKEN).build()

    register_admin_handlers(app)
    register_user_handlers(app)

    print("🎌 Anime Bot ishga tushdi!")

    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
    
