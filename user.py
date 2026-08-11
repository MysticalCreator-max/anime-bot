from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters
)
import database as db

# ═══ SOZLAMALAR ═══
CHANNEL_ID = "@Anifixel"  # Kanalингиз username

# ═══ KLAVIATURALAR ═══
def main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔍 Anime qidirish", callback_data="search"),
            InlineKeyboardButton("🆕 So'ngi animelar", callback_data="latest")
        ],
        [
            InlineKeyboardButton("📈 Eng ko'p ko'rilgan", callback_data="top"),
            InlineKeyboardButton("🎭 Janr bo'yicha", callback_data="genre")
        ],
        [
            InlineKeyboardButton("🔢 Kod orqali", callback_data="by_code"),
            InlineKeyboardButton("📺 Ongoing", callback_data="ongoing")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def genre_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Action", callback_data="genre_Action"),
            InlineKeyboardButton("Romance", callback_data="genre_Romance")
        ],
        [
            InlineKeyboardButton("Comedy", callback_data="genre_Comedy"),
            InlineKeyboardButton("Drama", callback_data="genre_Drama")
        ],
        [
            InlineKeyboardButton("Fantasy", callback_data="genre_Fantasy"),
            InlineKeyboardButton("Horror", callback_data="genre_Horror")
        ],
        [
            InlineKeyboardButton("Sci-Fi", callback_data="genre_Sci-Fi"),
            InlineKeyboardButton("Isekai", callback_data="genre_Isekai")
        ],
        [
            InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def not_subscribed_keyboard():
    keyboard = [
        [InlineKeyboardButton(
            "📢 Kanalga a'zo bo'lish",
            url=f"https://t.me/{CHANNEL_ID[1:]}"
        )],
        [InlineKeyboardButton(
            "✅ A'zo bo'ldim",
            callback_data="check_sub"
        )]
    ]
    return InlineKeyboardMarkup(keyboard)

# ═══ A'ZOLIK TEKSHIRISH ═══
async def check_subscription(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return True

# ═══ START ═══
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.add_user(user.id, user.username, user.full_name)
    
    is_sub = await check_subscription(context.bot, user.id)
    
    if not is_sub:
        await update.message.reply_text(
            "⚠️ Botdan foydalanish uchun kanalga a'zo bo'ling!",
            reply_markup=not_subscribed_keyboard()
        )
        return
    
    await update.message.reply_text(
        f"🎌 <b>Anime Bot ga xush kelibsiz!</b>\n\n"
        f"Salom, <b>{user.full_name}</b>! 👋\n\n"
        f"Quyidagi tugmalardan foydalaning:",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

# ═══ A'ZOLIKNI TEKSHIRISH ═══
async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    is_sub = await check_subscription(context.bot, query.from_user.id)
    
    if is_sub:
        await query.edit_message_text(
            f"🎌 <b>Anime Bot ga xush kelibsiz!</b>\n\n"
            f"Salom, <b>{query.from_user.full_name}</b>! 👋",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )
    else:
        await query.answer("❌ Hali a'zo bo'lmadingiz!", show_alert=True)

# ═══ ASOSIY MENU ═══
async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎌 <b>Asosiy menu</b>",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

# ═══ QIDIRISH ═══
async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['waiting_for'] = 'search'
    await query.edit_message_text(
        "🔍 <b>Anime nomini yozing:</b>",
        parse_mode="HTML"
    )

# ═══ KOD ORQALI ═══
async def by_code_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['waiting_for'] = 'code'
    await query.edit_message_text(
        "🔢 <b>Anime kodini yozing:</b>\n"
        "Masalan: <code>ANM001</code>",
        parse_mode="HTML"
    )

# ═══ MATN HANDLER ═══
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waiting = context.user_data.get('waiting_for')
    text = update.message.text
    
    if waiting == 'search':
        context.user_data['waiting_for'] = None
        await db.add_search(update.effective_user.id, text)
        results = await db.get_anime_by_title(text)
        
        if not results:
            await update.message.reply_text(
                f"❌ <b>'{text}'</b> bo'yicha hech narsa topilmadi!",
                parse_mode="HTML",
                reply_markup=main_keyboard()
            )
            return
        
        for anime in results[:5]:
            await send_anime_card(update.message, anime)
    
    elif waiting == 'code':
        context.user_data['waiting_for'] = None
        anime = await db.get_anime_by_code(text)
        
        if not anime:
            await update.message.reply_text(
                f"❌ <b>'{text}'</b> kodli anime topilmadi!",
                parse_mode="HTML",
                reply_markup=main_keyboard()
            )
            return
        
        await send_anime_card(update.message, anime)
    
    else:
        await db.add_search(update.effective_user.id, text)
        results = await db.get_anime_by_title(text)
        
        if not results:
            await update.message.reply_text(
                f"❌ <b>'{text}'</b> topilmadi!",
                parse_mode="HTML",
                reply_markup=main_keyboard()
            )
            return
        
        for anime in results[:5]:
            await send_anime_card(update.message, anime)

# ═══ SO'NGI ANIMELAR ═══
async def latest_animes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    animes = await db.get_latest_animes(10)
    
    if not animes:
        await query.edit_message_text(
            "❌ Hozircha anime yo'q!",
            reply_markup=main_keyboard()
        )
        return
    
    await query.edit_message_text("🆕 <b>So'ngi animelar:</b>", parse_mode="HTML")
    for anime in animes:
        await send_anime_card(query.message, anime)

# ═══ TOP ANIMELAR ═══
async def top_animes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    animes = await db.get_top_animes(10)
    
    if not animes:
        await query.edit_message_text(
            "❌ Hozircha anime yo'q!",
            reply_markup=main_keyboard()
        )
        return
    
    await query.edit_message_text("📈 <b>Eng ko'p ko'rilgan:</b>", parse_mode="HTML")
    for anime in animes:
        await send_anime_card(query.message, anime)

# ═══ JANR ═══
async def genre_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎭 <b>Janrni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=genre_keyboard()
    )

async def genre_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    genre = query.data.split("_")[1]
    animes = await db.get_animes_by_genre(genre)
    
    if not animes:
        await query.answer(f"❌ {genre} janrida anime yo'q!", show_alert=True)
        return
    
    await query.edit_message_text(
        f"🎭 <b>{genre} janridagi animelar:</b>",
        parse_mode="HTML"
    )
    for anime in animes[:5]:
        await send_anime_card(query.message, anime)

# ═══ ONGOING ═══
async def ongoing_animes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    animes = await db.get_ongoing_animes()
    
    if not animes:
        await query.edit_message_text(
            "❌ Hozircha ongoing anime yo'q!",
            reply_markup=main_keyboard()
        )
        return
    
    await query.edit_message_text(
        "📺 <b>Ongoing animelar:</b>",
        parse_mode="HTML"
    )
    for anime in animes:
        await send_anime_card(query.message, anime)

# ═══ ANIME CARD ═══
async def send_anime_card(message, anime):
    text = (
        f"🎌 <b>{anime[2]}</b>\n\n"
        f"🔢 Kod: <code>{anime[1]}</code>\n"
        f"🎭 Janr: {anime[4]}\n"
        f"📺 Status: {'🟢 Ongoing' if anime[8] == 'ongoing' else '✅ Tugagan'}\n"
        f"👁 Ko'rishlar: {anime[7]}\n\n"
        f"📝 {anime[3]}"
    )
    
    keyboard = [[InlineKeyboardButton("▶️ Ko'rish", callback_data=f"watch_{anime[1]}")]]
    markup = InlineKeyboardMarkup(keyboard)
    
    if anime[5]:
        await message.reply_photo(
            photo=anime[5],
            caption=text,
            parse_mode="HTML",
            reply_markup=markup
        )
    else:
        await message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=markup
        )

# ═══ ANIME KO'RISH ═══
async def watch_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    code = query.data.split("_")[1]
    anime = await db.get_anime_by_code(code)
    
    if not anime:
        await query.answer("❌ Anime topilmadi!", show_alert=True)
        return
    
    await db.update_anime_views(code)
    
    if anime[6]:
        await query.message.reply_video(
            video=anime[6],
            caption=f"🎌 <b>{anime[2]}</b>\n\n▶️ Tomosha qiling!",
            parse_mode="HTML"
        )
    else:
        await query.answer("❌ Bu anime uchun video yo'q!", show_alert=True)

# ═══ HANDLERLARNI RO'YXATDAN O'TKAZISH ═══
def register_user_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_sub_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(search_start, pattern="^search$"))
    app.add_handler(CallbackQueryHandler(by_code_start, pattern="^by_code$"))
    app.add_handler(CallbackQueryHandler(latest_animes, pattern="^latest$"))
    app.add_handler(CallbackQueryHandler(top_animes, pattern="^top$"))
    app.add_handler(CallbackQueryHandler(genre_list, pattern="^genre$"))
    app.add_handler(CallbackQueryHandler(genre_filter, pattern="^genre_"))
    app.add_handler(CallbackQueryHandler(ongoing_animes, pattern="^ongoing$"))
    app.add_handler(CallbackQueryHandler(watch_anime, pattern="^watch_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))