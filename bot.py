import os
import uuid
import qrcode
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

UPLOAD_FOLDER = 'uploads'
QR_FOLDER = 'qr_codes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 20 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    'pdf', 'docx', 'doc', 'xlsx', 'xls', 
    'jpg', 'jpeg', 'png', 'gif', 'bmp',
    'zip', 'rar', '7z', 'txt', 'pptx', 'ppt'
}

def get_base_url():
    """Get the base URL for file hosting"""
    replit_url = os.getenv('REPLIT_DEV_DOMAIN')
    if replit_url:
        return f"https://{replit_url}"
    return "http://localhost:5000"

def create_main_keyboard():
    """Create main inline keyboard"""
    keyboard = [
        [InlineKeyboardButton("📤 Fayl yuborish", callback_data='upload')],
        [InlineKeyboardButton("🧾 Bot haqida", callback_data='about')],
        [InlineKeyboardButton("📞 Aloqa", callback_data='contact')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_text = (
        "🌟 <b>Soliq.uz QR Fayl Bot</b>ga xush kelibsiz!\n\n"
        "Bu bot orqali siz:\n"
        "✅ Fayllarni yuklab, doimiy havola olishingiz\n"
        "✅ Faylga QR-kod yaratishingiz\n"
        "✅ QR-kodni skaner qilib faylni ochishingiz mumkin\n\n"
        "Quyidagi tugmalardan birini tanlang:"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=create_main_keyboard(),
        parse_mode='HTML'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'upload':
        text = (
            "📤 <b>Fayl yuklash</b>\n\n"
            "Quyidagi formatdagi fayllarni yuboring:\n"
            "📄 Hujjatlar: PDF, DOCX, XLSX, TXT\n"
            "🖼 Rasmlar: JPG, PNG, GIF, BMP\n"
            "📦 Arxivlar: ZIP, RAR, 7Z\n"
            "📊 Taqdimotlar: PPTX, PPT\n\n"
            "⚠️ Maksimal hajm: 20MB"
        )
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=create_main_keyboard())
    
    elif query.data == 'about':
        text = (
            "🧾 <b>Bot haqida</b>\n\n"
            "Soliq.uz QR Fayl Bot - bu fayllaringiz uchun QR-kod yaratuvchi xizmat.\n\n"
            "Bot fayllaringizni xavfsiz saqlaydi va har bir fayl uchun QR-kod yaratadi. "
            "QR-kodni skaner qilish orqali faylni osongina yuklab olish mumkin.\n\n"
            "🔒 Fayllaringiz xavfsiz saqlanadi\n"
            "⚡ Tez va qulay xizmat\n"
            "🆓 Bepul foydalanish"
        )
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=create_main_keyboard())
    
    elif query.data == 'contact':
        text = (
            "📞 <b>Aloqa</b>\n\n"
            "Savollaringiz bo'lsa, biz bilan bog'laning:\n\n"
            "📧 Email: support@soliq.uz\n"
            "🌐 Website: https://soliq.uz\n"
            "📱 Telegram: @soliq_support"
        )
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=create_main_keyboard())

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads"""
    message = update.message
    document = message.document
    
    if document.file_size > MAX_FILE_SIZE:
        await message.reply_text(
            "❌ Xatolik: Fayl hajmi 20MB dan oshmasligi kerak!",
            reply_markup=create_main_keyboard()
        )
        return
    
    file_extension = document.file_name.split('.')[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        await message.reply_text(
            f"❌ Xatolik: '{file_extension}' formatidagi fayllar qo'llab-quvvatlanmaydi!",
            reply_markup=create_main_keyboard()
        )
        return
    
    status_message = await message.reply_text("⏳ Fayl yuklanmoqda...")
    
    try:
        file = await context.bot.get_file(document.file_id)
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        await file.download_to_drive(file_path)
        
        file_url = f"{get_base_url()}/files/{unique_filename}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(file_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        await status_message.edit_text("✅ Fayl muvaffaqiyatly yuklandi!")
        
        success_text = (
            f"✅ <b>Faylingiz muvaffaqiyatli yuklandi!</b>\n\n"
            f"📄 Fayl nomi: {document.file_name}\n"
            f"📊 Hajmi: {document.file_size / 1024:.2f} KB\n\n"
            f"🔗 <b>Faylga havola:</b>\n{file_url}\n\n"
            f"📎 QR-kodni skaner qiling yoki havolani bosing:"
        )
        
        await message.reply_text(success_text, parse_mode='HTML')
        
        await message.reply_photo(
            photo=img_byte_arr,
            caption=f"📱 QR-kodni skaner qilish orqali faylni oching\n🌐 Soliq.uz",
            reply_markup=create_main_keyboard()
        )
        
    except Exception as e:
        await status_message.edit_text(
            f"❌ Xatolik yuz berdi: {str(e)}",
            reply_markup=create_main_keyboard()
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads"""
    message = update.message
    photo = message.photo[-1]
    
    if photo.file_size > MAX_FILE_SIZE:
        await message.reply_text(
            "❌ Xatolik: Rasm hajmi 20MB dan oshmasligi kerak!",
            reply_markup=create_main_keyboard()
        )
        return
    
    status_message = await message.reply_text("⏳ Rasm yuklanmoqda...")
    
    try:
        file = await context.bot.get_file(photo.file_id)
        unique_filename = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        await file.download_to_drive(file_path)
        
        file_url = f"{get_base_url()}/files/{unique_filename}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(file_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        await status_message.edit_text("✅ Rasm muvaffaqiyatly yuklandi!")
        
        success_text = (
            f"✅ <b>Rasmingiz muvaffaqiyatli yuklandi!</b>\n\n"
            f"📊 Hajmi: {photo.file_size / 1024:.2f} KB\n\n"
            f"🔗 <b>Rasmga havola:</b>\n{file_url}\n\n"
            f"📎 QR-kodni skaner qiling yoki havolani bosing:"
        )
        
        await message.reply_text(success_text, parse_mode='HTML')
        
        await message.reply_photo(
            photo=img_byte_arr,
            caption=f"📱 QR-kodni skaner qilish orqali rasmni oching\n🌐 Soliq.uz",
            reply_markup=create_main_keyboard()
        )
        
    except Exception as e:
        await status_message.edit_text(
            f"❌ Xatolik yuz berdi: {str(e)}",
            reply_markup=create_main_keyboard()
        )

def main():
    """Main function to run the bot"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN muhit o'zgaruvchisi topilmadi!")
        print("📝 Botni ishga tushirish uchun Telegram Bot Token kerak.")
        return
    
    application = Application.builder().token(bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("🤖 Bot ishga tushdi! Fayllarni qabul qilish uchun tayyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
