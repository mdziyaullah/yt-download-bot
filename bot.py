from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp
from telegram.ext import CommandHandler

TOKEN = "8652648742:AAEkpHJw0kJrnxPoVC_otZvghRN__tbL_RU"

video_cache = {}

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    ydl_opts = {'quiet': True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = []
    keyboard = []

    for f in info['formats']:
        if f.get('height') in [360, 720, 1080] and f.get('url'):
            formats.append(f)
            keyboard.append([InlineKeyboardButton(f"{f['height']}p", callback_data=str(len(formats)-1))])

    video_cache[update.message.chat_id] = formats

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select quality:", reply_markup=reply_markup)
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\nPlease send a video link (YouTube / Instagram / Facebook) to download."
    )

async def quality_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    index = int(query.data)
    formats = video_cache.get(query.message.chat_id)

    if formats:
        url = formats[index]['url']
        await query.message.reply_text(f"Download link:\n{url}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(quality_selected))

app.run_polling()

