import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== KONFIGURATSIYA ==========
TOKEN = "8908378797:AAEgvugCjaCIOWQGlCfC2bKKhLAzRb8csKk"  # @BotFather dan olingan token
ADMIN_ID = 267256427  # Sizning Telegram ID'ingiz (admin)

# Ma'lumotlarni saqlash
DATA_FILE = "chat_links.json"
chat_links = {}  # {admin_message_id: user_id}
user_names = {}  # {user_id: full_name}

# ========== YORDAMCHI FUNKSIYALAR ==========
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
    data = {
        'chat_links': chat_links,
        'user_names': user_names
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# ========== BOT BUYRUQLARI ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start - AI Helper"""
    user = update.effective_user
    user_id = user.id
    user_name = user.full_name
    
    # Foydalanuvchini saqlash
    if str(user_id) not in user_names:
        user_names[str(user_id)] = user_name
        save_data()
        
        # Admin'ga yangi foydalanuvchi haqida xabar
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🆕 **Yangi foydalanuvchi!**\n👤 {user_name}\n🆔 `{user_id}`",
            parse_mode='Markdown'
        )
    
    await update.message.reply_text("🔒 AI Helper")

async def clear_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/clear - barcha xabarlarni o'chirish (faqat admin)"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    global chat_links, user_names
    chat_links = {}
    user_names = {}
    save_data()
    await update.message.reply_text("✅ Barcha ma'lumotlar o'chirildi!")

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchilar ro'yxati (faqat admin)"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not user_names:
        await update.message.reply_text("📭 Hozircha foydalanuvchi yo'q")
        return
    
    text = "📋 **Foydalanuvchilar:**\n\n"
    for uid, name in user_names.items():
        text += f"👤 {name}\n🆔 `{uid}`\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

# ========== FOYDALANUVCHI XABARI ==========
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi xabari - ism va ID bilan birga keladi"""
    user = update.effective_user
    user_id = user.id
    user_name = user.full_name
    message = update.message
    
    # Foydalanuvchini saqlash (agar start bosmagan bo'lsa ham)
    if str(user_id) not in user_names:
        user_names[str(user_id)] = user_name
        save_data()
    
    # Admin'ga xabar yuborish (ism va ID bilan birga)
    try:
        if message.text:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 {user_name}\n🆔 `{user_id}`\n\n💬 {message.text}",
                parse_mode='Markdown'
            )
            # Xabar ID ni saqlash (javob berish uchun)
            # Bu yerda message_id ni olish murakkab, keyingi xatboshida to'g'rilaymiz
            
        elif message.photo:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=message.photo[-1].file_id,
                caption=f"👤 {user_name}\n🆔 `{user_id}`\n\n📷 Rasm yubordi",
                parse_mode='Markdown'
            )
            
        elif message.document:
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=message.document.file_id,
                caption=f"👤 {user_name}\n🆔 `{user_id}`\n\n📎 Fayl: {message.document.file_name}",
                parse_mode='Markdown'
            )
            
        elif message.video:
            await context.bot.send_video(
                chat_id=ADMIN_ID,
                video=message.video.file_id,
                caption=f"👤 {user_name}\n🆔 `{user_id}`\n\n🎥 Video yubordi",
                parse_mode='Markdown'
            )
            
        elif message.voice:
            await context.bot.send_voice(
                chat_id=ADMIN_ID,
                voice=message.voice.file_id
            )
            # Ovozli xabar uchun alohida captionsiz yuboramiz
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 {user_name}\n🆔 `{user_id}`\n\n🎤 Ovozli xabar yubordi",
                parse_mode='Markdown'
            )
            
        elif message.sticker:
            await context.bot.send_sticker(
                chat_id=ADMIN_ID,
                sticker=message.sticker.file_id
            )
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 {user_name}\n🆔 `{user_id}`\n\n🔹 Stiker yubordi",
                parse_mode='Markdown'
            )
            
        # Foydalanuvchiga hech qanday "xabar yuborildi" degan xabar YO'Q!
        
    except Exception as e:
        print(f"Xatolik: {e}")

# ========== TO'G'RI ADMIN JAVOBI (message_id bilan) ==========
# Bu funksiya to'g'ri ishlashi uchun message_id ni saqlash kerak

# Yaxshilangan versiya - xabar ID larni saqlaymiz
async def user_message_with_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi xabari - ID saqlangan holda"""
    user = update.effective_user
    user_id = user.id
    user_name = user.full_name
    message = update.message
    
    if str(user_id) not in user_names:
        user_names[str(user_id)] = user_name
        save_data()
    
    try:
        if message.text:
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 {user_name}\n🆔 `{user_id}`\n\n💬 {message.text}",
                parse_mode='Markdown'
            )
            # Xabar ID ni saqlash
            chat_links[str(sent.message_id)] = user_id
            save_data()
            
        elif message.photo:
            sent = await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=message.photo[-1].file_id,
                caption=f"👤 {user_name}\n🆔 `{user_id}`\n\n📷 Rasm yubordi",
                parse_mode='Markdown'
            )
            chat_links[str(sent.message_id)] = user_id
            save_data()
            
        elif message.document:
            sent = await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=message.document.file_id,
                caption=f"👤 {user_name}\n🆔 `{user_id}`\n\n📎 Fayl: {message.document.file_name}",
                parse_mode='Markdown'
            )
            chat_links[str(sent.message_id)] = user_id
            save_data()
            
        elif message.video:
            sent = await context.bot.send_video(
                chat_id=ADMIN_ID,
                video=message.video.file_id,
                caption=f"👤 {user_name}\n🆔 `{user_id}`\n\n🎥 Video yubordi",
                parse_mode='Markdown'
            )
            chat_links[str(sent.message_id)] = user_id
            save_data()
            
        elif message.voice:
            # Ovozli xabar uchun audio yuboramiz
            await context.bot.send_voice(
                chat_id=ADMIN_ID,
                voice=message.voice.file_id
            )
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 {user_name}\n🆔 `{user_id}`\n\n🎤 Ovozli xabar yubordi",
                parse_mode='Markdown'
            )
            chat_links[str(sent.message_id)] = user_id
            save_data()
            
        elif message.sticker:
            await context.bot.send_sticker(
                chat_id=ADMIN_ID,
                sticker=message.sticker.file_id
            )
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 {user_name}\n🆔 `{user_id}`\n\n🔹 Stiker yubordi",
                parse_mode='Markdown'
            )
            chat_links[str(sent.message_id)] = user_id
            save_data()
        
        # Foydalanuvchiga hech qanday xabar YO'Q!
        
    except Exception as e:
        print(f"Xatolik: {e}")

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin javobi - faqat xabar, hech qanday ma'lumotsiz"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    message = update.message
    
    # Agar reply qilingan bo'lsa
    if message.reply_to_message:
        original_msg_id = str(message.reply_to_message.message_id)
        
        if original_msg_id in chat_links:
            target_user_id = chat_links[original_msg_id]
            
            try:
                # Javobni oddiy xabar sifatida (hech qanday ma'lumotsiz)
                if message.text:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=message.text
                    )
                    
                elif message.photo:
                    await context.bot.send_photo(
                        chat_id=target_user_id,
                        photo=message.photo[-1].file_id
                    )
                    
                elif message.document:
                    await context.bot.send_document(
                        chat_id=target_user_id,
                        document=message.document.file_id
                    )
                    
                elif message.video:
                    await context.bot.send_video(
                        chat_id=target_user_id,
                        video=message.video.file_id
                    )
                    
                elif message.voice:
                    await context.bot.send_voice(
                        chat_id=target_user_id,
                        voice=message.voice.file_id
                    )
                    
                elif message.sticker:
                    await context.bot.send_sticker(
                        chat_id=target_user_id,
                        sticker=message.sticker.file_id
                    )
                
                # Admin'ga "javob yuborildi" degan xabar YO'Q!
                
            except Exception as e:
                print(f"Javob yuborishda xatolik: {e}")
    else:
        # Agar reply qilinmagan bo'lsa, eslatma (bu faqat admin'ga ko'rinadi)
        await message.reply_text("ℹ️ Javob berish uchun xabarni REPLY qiling", reply_to_message_id=message.message_id)

# ========== ASOSIY FUNKSIYA ==========
def main():
    load_data()
    print(f"📂 Yuklandi: {len(chat_links)} ta chat aloqasi")
    print(f"👥 {len(user_names)} ta foydalanuvchi")
    
    application = Application.builder().token(TOKEN).build()
    
    # Buyruqlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_all))
    application.add_handler(CommandHandler("users", users_list))
    
    # Xabar handlerlari
    application.add_handler(MessageHandler(filters.User(ADMIN_ID) & ~filters.COMMAND, admin_reply))
    application.add_handler(MessageHandler(~filters.User(ADMIN_ID) & ~filters.COMMAND, user_message_with_id))
    
    print("🤖 Maxfiy chat bot ishga tushdi...")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("✅ Bot tayyor!")
    print("\n📌 QOIDALAR:")
    print("- Foydalanuvchi xabari: Ism + ID + Xabar birga keladi")
    print("- Admin javobi: Faqat xabar (hech qanday ma'lumotsiz)")
    print("- Javob berish uchun xabarni REPLY qiling")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()