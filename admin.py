from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ConversationHandler, filters
)
import database as db

# ═══ ADMIN ID ═══
ADMIN_ID = 6832985197  # main.py dagi bilan bir xil

# ═══ STATES ═══
(ADD_CODE, ADD_TITLE, ADD_DESC, ADD_GENRE,
 ADD_PHOTO, ADD_VIDEO, ADD_STATUS,
 EDIT_CODE, EDIT_TITLE, EDIT_DESC, EDIT_GENRE, EDIT_STATUS,
 DELETE_CODE, BROADCAST_MSG) = range(14)

# ═══ KLAVIATURALAR ═══
def admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ Anime yuklash", callback_data="add_anime"),
            InlineKeyboardButton("✏️ Tahrirlash", callback_data="edit_anime")
        ],
        [
            InlineKeyboardButton("🗑 O'chirish", callback_data="delete_anime"),
            InlineKeyboardButton("📊 Statistika", callback_data="statistics")
        ],
        [
            InlineKeyboardButton("📢 Xabar yuborish", callback_data="broadcast"),
            InlineKeyboardButton("🔔 Yangi qism", callback_data="new_episode")
        ],
        [
            InlineKeyboardButton("⭐ Post yuborish", callback_data="send_post")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def cancel_keyboard():
    keyboard = [[InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_conv")]]
    return InlineKeyboardMarkup(keyboard)

def status_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("✅ Tugagan", callback_data="status_completed"),
            InlineKeyboardButton("🟢 Ongoing", callback_data="status_ongoing")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ═══ ADMIN TEKSHIRISH ═══
def is_admin(user_id):
    return user_id == ADMIN_ID

# ═══ ADMIN PANEL ═══
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    await update.message.reply_text(
        "🛠 <b>Admin Panel</b>\n\nKerakli bo'limni tanlang:",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )

# ═══ STATISTIKA ═══
async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    users = await db.get_users_count()
    animes = await db.get_animes_count()
    searches = await db.get_searches_count()
    
    await query.edit_message_text(
        f"📊 <b>Statistika</b>\n\n"
        f"👤 Foydalanuvchilar: <b>{users}</b>\n"
        f"🎌 Animelar: <b>{animes}</b>\n"
        f"🔍 Qidiruvlar: <b>{searches}</b>",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )

# ═══ ANIME QO'SHISH ═══
async def add_anime_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔢 <b>Anime kodini yozing:</b>\n"
        "Masalan: <code>ANM001</code>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return ADD_CODE

async def add_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    existing = await db.get_anime_by_code(update.message.text)
    if existing:
        await update.message.reply_text(
            "❌ Bu kod mavjud! Boshqa kod yozing:",
            reply_markup=cancel_keyboard()
        )
        return ADD_CODE
    
    context.user_data['code'] = update.message.text
    await update.message.reply_text(
        "📝 <b>Anime nomini yozing:</b>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return ADD_TITLE

async def add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text
    await update.message.reply_text(
        "📄 <b>Tavsifini yozing:</b>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return ADD_DESC

async def add_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text
    await update.message.reply_text(
        "🎭 <b>Janrini yozing:</b>\n"
        "Masalan: <code>Action, Comedy</code>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return ADD_GENRE

async def add_genre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['genre'] = update.message.text
    await update.message.reply_text(
        "🖼 <b>Rasm yuboring:</b>\n"
        "O'tkazib yuborish: /skip",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return ADD_PHOTO

async def add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo_id'] = update.message.photo[-1].file_id
    await update.message.reply_text(
        "🎬 <b>Video yuboring:</b>\n"
        "O'tkazib yuborish: /skip",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return ADD_VIDEO

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo_id'] = None
    await update.message.reply_text(
        "🎬 <b>Video yuboring:</b>\n"
        "O'tkazib yuborish: /skip",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return ADD_VIDEO

async def add_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['video_id'] = update.message.video.file_id
    await update.message.reply_text(
        "📺 <b>Statusni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=status_keyboard()
    )
    return ADD_STATUS

async def skip_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['video_id'] = None
    await update.message.reply_text(
        "📺 <b>Statusni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=status_keyboard()
    )
    return ADD_STATUS

async def add_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    status = query.data.split("_")[1]
    d = context.user_data
    
    await db.add_anime(
        d['code'], d['title'], d['description'],
        d['genre'], d.get('photo_id'), d.get('video_id'), status
    )
    
    await query.edit_message_text(
        f"✅ <b>Anime yuklandi!</b>\n\n"
        f"🔢 Kod: <code>{d['code']}</code>\n"
        f"📝 Nom: {d['title']}",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )
    return ConversationHandler.END

# ═══ ANIME O'CHIRISH ═══
async def delete_anime_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🗑 <b>O'chirish uchun kodni yozing:</b>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return DELETE_CODE

async def delete_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    anime = await db.get_anime_by_code(update.message.text)
    if not anime:
        await update.message.reply_text(
            "❌ Bunday anime topilmadi!",
            reply_markup=cancel_keyboard()
        )
        return DELETE_CODE
    
    await db.delete_anime(update.message.text)
    await update.message.reply_text(
        f"✅ <b>{anime[2]}</b> o'chirildi!",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )
    return ConversationHandler.END

# ═══ ANIME TAHRIRLASH ═══
async def edit_anime_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✏️ <b>Tahrirlash uchun kodni yozing:</b>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return EDIT_CODE

async def edit_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    anime = await db.get_anime_by_code(update.message.text)
    if not anime:
        await update.message.reply_text(
            "❌ Bunday anime topilmadi!",
            reply_markup=cancel_keyboard()
        )
        return EDIT_CODE
    
    context.user_data['edit_code'] = update.message.text
    await update.message.reply_text(
        f"📝 <b>Yangi nomini yozing:</b>\n"
        f"Hozirgi: <b>{anime[2]}</b>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return EDIT_TITLE

async def edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_title'] = update.message.text
    await update.message.reply_text(
        "📄 <b>Yangi tavsifini yozing:</b>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return EDIT_DESC

async def edit_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_desc'] = update.message.text
    await update.message.reply_text(
        "🎭 <b>Yangi janrini yozing:</b>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return EDIT_GENRE

async def edit_genre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_genre'] = update.message.text
    await update.message.reply_text(
        "📺 <b>Yangi statusni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=status_keyboard()
    )
    return EDIT_STATUS

async def edit_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    status = query.data.split("_")[1]
    d = context.user_data
    
    await db.update_anime(
        d['edit_code'], d['edit_title'],
        d['edit_desc'], d['edit_genre'], status
    )
    
    await query.edit_message_text(
        f"✅ <b>Anime tahrirlandi!</b>\n\n"
        f"🔢 Kod: <code>{d['edit_code']}</code>\n"
        f"📝 Nom: {d['edit_title']}",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )
    return ConversationHandler.END

# ═══ XABAR YUBORISH ═══
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['broadcast_type'] = 'broadcast'
    await query.edit_message_text(
        "📢 <b>Barcha foydalanuvchilarga xabar yozing:</b>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return BROADCAST_MSG

async def new_episode_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['broadcast_type'] = 'episode'
    await query.edit_message_text(
        "🔔 <b>Yangi qism haqida xabar yozing:</b>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return BROADCAST_MSG

async def send_post_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['broadcast_type'] = 'post'
    await query.edit_message_text(
        "⭐ <b>Post yuboring (rasm, video yoki matn):</b>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    return BROADCAST_MSG

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await db.get_all_users()
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await update.message.forward(user_id)
            success += 1
        except:
            failed += 1
    
    await update.message.reply_text(
        f"✅ <b>Yuborildi!</b>\n\n"
        f"✔️ Muvaffaqiyatli: {success}\n"
        f"❌ Yuborilmadi: {failed}",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )
    return ConversationHandler.END

# ═══ BEKOR QILISH ═══
async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🛠 <b>Admin Panel</b>",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )
    return ConversationHandler.END

# ═══ HANDLERLARNI RO'YXATDAN O'TKAZISH ═══
def register_admin_handlers(app):
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(statistics, pattern="^statistics$"))
    
    # Anime qo'shish
    add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_anime_start, pattern="^add_anime$")],
        states={
            ADD_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_code)],
            ADD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_title)],
            ADD_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_desc)],
            ADD_GENRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_genre)],
            ADD_PHOTO: [
                MessageHandler(filters.PHOTO, add_photo),
                CommandHandler("skip", skip_photo)
            ],
            ADD_VIDEO: [
                MessageHandler(filters.VIDEO, add_video),
                CommandHandler("skip", skip_video)
            ],
            ADD_STATUS: [CallbackQueryHandler(add_status, pattern="^status_")]
        },
        fallbacks=[CallbackQueryHandler(cancel_conv, pattern="^cancel_conv$")]
    )
    
    # Anime o'chirish
    delete_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(delete_anime_start, pattern="^delete_anime$")],
        states={
            DELETE_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_anime)]
        },
        fallbacks=[CallbackQueryHandler(cancel_conv, pattern="^cancel_conv$")]
    )
    
    # Anime tahrirlash
    edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_anime_start, pattern="^edit_anime$")],
        states={
            EDIT_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_code)],
            EDIT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_title)],
            EDIT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_desc)],
            EDIT_GENRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_genre)],
            EDIT_STATUS: [CallbackQueryHandler(edit_status, pattern="^status_")]
        },
        fallbacks=[CallbackQueryHandler(cancel_conv, pattern="^cancel_conv$")]
    )
    
    # Broadcast
    broadcast_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(broadcast_start, pattern="^broadcast$"),
            CallbackQueryHandler(new_episode_start, pattern="^new_episode$"),
            CallbackQueryHandler(send_post_start, pattern="^send_post$")
        ],
        states={
            BROADCAST_MSG: [
                MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_send)
            ]
        },
        fallbacks=[CallbackQueryHandler(cancel_conv, pattern="^cancel_conv$")]
    )
    
    app.add_handler(add_conv)
    app.add_handler(delete_conv)
    app.add_handler(edit_conv)
    app.add_handler(broadcast_conv)