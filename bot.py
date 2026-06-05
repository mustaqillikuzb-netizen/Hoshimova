import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

TOKEN = "8908378797:AAEgvugCjaCIOWQGlCfC2bKKhLAzRb8csKk"
ADMIN_ID = 267256427

DATA_FILE = "chat_links.json"
chat_links = {}
user_names = {}

flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Bot running", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)

def load_data():
    global chat_links, user_names
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            chat_links = data.get('chat_links', {})
            user_names = data.get('user_names', {})
    else:
        chat_links = {}
        user_names = {}

def save_data():
    data = {'chat_links': chat_links, 'user_names': user_names}
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_name = user.full_name
    if str(user_id) not in user_names:
        user_names[str(user_id)] = user_name
        save_data()
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🆕 Yangi foydalanuvchi: {user_name}\nID: {user_id}")
    await update.message.reply_text("🔒 Bot ishlayapti. Xabarlaringiz adminga boradi.")

async def clear_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    global chat_links, user_names
    chat_links = {}
    user_names = {}
    save_data()
    await update.message.reply_text("✅ Barcha ma'lumotlar o'chirildi!")

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not user_names:
        await update.message.reply_text("📭 Hozircha foydalanuvchi yo'q")
        return
    text = "📋 Foydalanuvchilar:\n\n"
    for uid, name in user_names.items():
        text += f"👤 {name}\n🆔 {uid}\n\n"
    await update.message.reply_text(text)

async def user_message_with_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_name = user.full_name
    msg = update.message
    if str(user_id) not in user_names:
        user_names[str(user_id)] = user_name
        save_data()
    try:
        if msg.text:
            sent = await context.bot.send_message(chat_id=ADMIN_ID, text=f"👤 {user_name}\n🆔 {user_id}\n\n💬 {msg.text}")
            chat_links[str(sent.message_id)] = user_id
            save_data()
        elif msg.photo:
            sent = await context.bot.send_photo(chat_id=ADMIN_ID, photo=msg.photo[-1].file_id, caption=f"👤 {user_name}\n🆔 {user_id}\n\n📷 Rasm")
            chat_links[str(sent.message_id)] = user_id
            save_data()
        elif msg.document:
            sent = await context.bot.send_document(chat_id=ADMIN_ID, document=msg.document.file_id, caption=f"👤 {user_name}\n🆔 {user_id}\n\n📎 {msg.document.file_name}")
            chat_links[str(sent.message_id)] = user_id
            save_data()
        elif msg.video:
            sent = await context.bot.send_video(chat_id=ADMIN_ID, video=msg.video.file_id, caption=f"👤 {user_name}\n🆔 {user_id}\n\n🎥 Video")
            chat_links[str(sent.message_id)] = user_id
            save_data()
        elif msg.voice:
            await context.bot.send_voice(chat_id=ADMIN_ID, voice=msg.voice.file_id)
            sent = await context.bot.send_message(chat_id=ADMIN_ID, text=f"👤 {user_name}\n🆔 {user_id}\n\n🎤 Ovoz")
            chat_links[str(sent.message_id)] = user_id
            save_data()
        elif msg.sticker:
            await context.bot.send_sticker(chat_id=ADMIN_ID, sticker=msg.sticker.file_id)
            sent = await context.bot.send_message(chat_id=ADMIN_ID, text=f"👤 {user_name}\n🆔 {user_id}\n\n🔹 Stiker")
            chat_links[str(sent.message_id)] = user_id
            save_data()
    except Exception as e:
        print(f"Xato: {e}")

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = update.message
    if msg.reply_to_message:
        orig_id = str(msg.reply_to_message.message_id)
        if orig_id in chat_links:
            target = chat_links[orig_id]
            try:
                if msg.text:
                    await context.bot.send_message(chat_id=target, text=msg.text)
                elif msg.photo:
                    await context.bot.send_photo(chat_id=target, photo=msg.photo[-1].file_id)
                elif msg.document:
                    await context.bot.send_document(chat_id=target, document=msg.document.file_id)
                elif msg.video:
                    await context.bot.send_video(chat_id=target, video=msg.video.file_id)
                elif msg.voice:
                    await context.bot.send_voice(chat_id=target, voice=msg.voice.file_id)
                elif msg.sticker:
                    await context.bot.send_sticker(chat_id=target, sticker=msg.sticker.file_id)
            except Exception as e:
                print(f"Javob xatosi: {e}")
    else:
        await msg.reply_text("ℹ️ Javob berish uchun REPLY qiling")

def main():
    load_data()
    print(f"📂 Yuklandi: {len(chat_links)} ta chat")
    print(f"👥 {len(user_names)} ta foydalanuvchi")
    
    threading.Thread(target=run_flask).start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_all))
    app.add_handler(CommandHandler("users", users_list))
    app.add_handler(MessageHandler(filters.User(ADMIN_ID) & ~filters.COMMAND, admin_reply))
    app.add_handler(MessageHandler(~filters.User(ADMIN_ID) & ~filters.COMMAND, user_message_with_id))
    
    print("🤖 Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
