from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

ADMIN_CHAT_ID = 1612270615
TOKEN = "7754620943:AAESsQB-tTOxNlpgr9yfhieOR5ua4enR5DU"

app = Flask(__name__)

# Telegram Application yaratamiz
application = Application.builder().token(TOKEN).build()

# --------------------
# Telegram handlerlar
# --------------------
async def start(update, context):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Siz admin emassiz!")
        return
    await update.message.reply_text("✅ Bot webhook orqali ishlayapti!")

application.add_handler(CommandHandler("start", start))

# --------------------
# Flask route (webhook uchun)
# --------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok", 200

# --------------------
# Test uchun
# --------------------
@app.route("/")
def index():
    return "Bot ishlayapti (webhook rejimi)"
