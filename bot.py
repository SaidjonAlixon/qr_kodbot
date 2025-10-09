import os
import uuid
import qrcode
import io
import logging
import subprocess
from pdf2docx import Converter
from docx import Document
from docx.shared import Inches, Pt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.error import BadRequest, Conflict

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
        [InlineKeyboardButton("🔄 PDF ↔ Word", callback_data='convert_menu')],
        [InlineKeyboardButton("📋 Word faylga QR qo'shish", callback_data='add_qr_to_word')],
        [InlineKeyboardButton("🧾 Bot haqida", callback_data='about')],
        [InlineKeyboardButton("📞 Aloqa", callback_data='contact')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_convert_keyboard():
    """Create conversion menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📄 PDF → Word", callback_data='pdf_to_word')],
        [InlineKeyboardButton("📝 Word → PDF", callback_data='word_to_pdf')],
        [InlineKeyboardButton("◀️ Orqaga", callback_data='back_to_main')]
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
        keyboard = create_main_keyboard()
    elif query.data == 'convert_menu':
        text = (
            "🔄 <b>PDF ↔ Word Konvertatsiya</b>\n\n"
            "Quyidagi konvertatsiya turlaridan birini tanlang:\n\n"
            "📄 <b>PDF → Word</b>\n"
            "PDF faylni DOCX formatiga o'zgartirish\n\n"
            "📝 <b>Word → PDF</b>\n"
            "DOCX faylni PDF formatiga o'zgartirish\n\n"
            "⚠️ Maksimal hajm: 20MB"
        )
        keyboard = create_convert_keyboard()
    elif query.data == 'pdf_to_word':
        context.user_data['convert_mode'] = 'pdf_to_word'
        text = (
            "📄 <b>PDF → Word</b>\n\n"
            "Iltimos PDF faylni yuboring.\n"
            "Fayl DOCX formatiga o'zgartiriladi.\n\n"
            "⚠️ Maksimal hajm: 20MB"
        )
        keyboard = create_convert_keyboard()
    elif query.data == 'word_to_pdf':
        context.user_data['convert_mode'] = 'word_to_pdf'
        text = (
            "📝 <b>Word → PDF</b>\n\n"
            "Iltimos DOCX yoki DOC faylni yuboring.\n"
            "Fayl PDF formatiga o'zgartiriladi.\n\n"
            "⚠️ Maksimal hajm: 20MB"
        )
        keyboard = create_convert_keyboard()
    elif query.data == 'add_qr_to_word':
        context.user_data['convert_mode'] = 'add_qr_to_word'
        text = (
            "📋 <b>Word faylga QR kod qo'shish</b>\n\n"
            "Iltimos DOCX faylni yuboring.\n"
            "Fayl ichiga QR kod qo'shiladi va qaytariladi.\n\n"
            "📱 QR kodni skanerlash orqali faylga kirish mumkin!\n\n"
            "⚠️ Faqat DOCX format qabul qilinadi\n"
            "⚠️ Maksimal hajm: 20MB"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Orqaga", callback_data='back_to_main')]])
    elif query.data == 'back_to_main':
        context.user_data['convert_mode'] = None
        text = (
            "🌟 <b>Soliq.uz QR Fayl Bot</b>\n\n"
            "Quyidagi tugmalardan birini tanlang:"
        )
        keyboard = create_main_keyboard()
    elif query.data == 'about':
        text = (
            "🧾 <b>Bot haqida</b>\n\n"
            "Soliq.uz QR Fayl Bot - bu fayllaringiz uchun QR-kod yaratuvchi va "
            "PDF/Word konvertatsiya xizmati.\n\n"
            "🔄 PDF va Word formatlarini o'zgartiring\n"
            "🔒 Fayllaringiz xavfsiz saqlanadi\n"
            "⚡ Tez va qulay xizmat\n"
            "🆓 Bepul foydalanish"
        )
        keyboard = create_main_keyboard()
    elif query.data == 'contact':
        text = (
            "📞 <b>Aloqa</b>\n\n"
            "Savollaringiz bo'lsa, biz bilan bog'laning:\n\n"
            "📧 Email: support@soliq.uz\n"
            "🌐 Website: https://soliq.uz\n"
            "📱 Telegram: @soliq_support"
        )
        keyboard = create_main_keyboard()
    else:
        return
    
    try:
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=keyboard)
    except BadRequest as e:
        if "message is not modified" in str(e).lower():
            logger.info("Xabar allaqachon bir xil, o'zgartirish kerak emas")
        else:
            logger.error(f"Tugma bosilishida xatolik: {e}")

async def convert_pdf_to_word(pdf_path, docx_path):
    """Convert PDF to Word using pdf2docx"""
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return True
    except Exception as e:
        logger.error(f"PDF to Word konvertatsiya xatoligi: {e}")
        return False

async def convert_word_to_pdf(docx_path, pdf_path):
    """Convert Word to PDF using LibreOffice"""
    try:
        output_dir = os.path.dirname(pdf_path)
        soffice_path = subprocess.run(
            ['which', 'soffice'],
            capture_output=True,
            text=True
        ).stdout.strip() or '/nix/store/s77ki6j3if918jk373md4aajqii531rd-libreoffice-24.8.7.2-wrapped/bin/soffice'
        
        result = subprocess.run(
            [soffice_path, '--headless', '--convert-to', 'pdf', '--outdir', output_dir, docx_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return True
        else:
            logger.error(f"LibreOffice xatoligi: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("Word to PDF konvertatsiya vaqti tugadi")
        return False
    except Exception as e:
        logger.error(f"Word to PDF konvertatsiya xatoligi: {e}")
        return False

async def add_qr_to_word_document(docx_path, qr_image_path, output_path):
    """Add QR code to Word document"""
    try:
        doc = Document(docx_path)
        
        # Add QR code image at the end of document (centered, 1x1 inches)
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run()
        run.add_picture(qr_image_path, width=Inches(1), height=Inches(1))
        
        # Add footer to the document (all sections)
        for section in doc.sections:
            footer = section.footer
            footer_paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
            footer_paragraph.text = 'DIDOX.UZ Orqali tasdiqlandi!'
            footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Save document
        doc.save(output_path)
        return True
    except Exception as e:
        logger.error(f"Word faylga QR qo'shish xatoligi: {e}")
        return False

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
    convert_mode = context.user_data.get('convert_mode')
    
    if convert_mode == 'pdf_to_word':
        if file_extension != 'pdf':
            await message.reply_text(
                "❌ Xatolik: Iltimos PDF fayl yuboring!",
                reply_markup=create_convert_keyboard()
            )
            return
        
        status_message = await message.reply_text("⏳ PDF Word ga o'zgartrilmoqda...")
        
        pdf_path = None
        docx_path = None
        try:
            file = await context.bot.get_file(document.file_id)
            unique_id = str(uuid.uuid4())
            pdf_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.pdf")
            docx_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.docx")
            
            await file.download_to_drive(pdf_path)
            
            success = await convert_pdf_to_word(pdf_path, docx_path)
            
            if success and os.path.exists(docx_path):
                await status_message.edit_text("✅ Konvertatsiya muvaffaqiyatli!")
                
                with open(docx_path, 'rb') as docx_file:
                    await message.reply_document(
                        document=docx_file,
                        filename=f"{os.path.splitext(document.file_name)[0]}.docx",
                        caption="✅ PDF Word formatiga o'zgartirildi\n🌐 Soliq.uz",
                        reply_markup=create_convert_keyboard()
                    )
                context.user_data['convert_mode'] = None
            else:
                await status_message.edit_text(
                    "❌ Konvertatsiya xatoligi. Iltimos qaytadan urinib ko'ring.",
                    reply_markup=create_convert_keyboard()
                )
        except Exception as e:
            logger.error(f"PDF to Word handler xatoligi: {e}")
            await status_message.edit_text(
                f"❌ Xatolik yuz berdi: {str(e)}",
                reply_markup=create_convert_keyboard()
            )
        finally:
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)
            if docx_path and os.path.exists(docx_path):
                os.remove(docx_path)
        return
    
    elif convert_mode == 'word_to_pdf':
        if file_extension not in ['docx', 'doc']:
            await message.reply_text(
                "❌ Xatolik: Iltimos DOCX yoki DOC fayl yuboring!",
                reply_markup=create_convert_keyboard()
            )
            return
        
        status_message = await message.reply_text("⏳ Word PDF ga o'zgartrilmoqda...")
        
        docx_path = None
        pdf_path = None
        try:
            file = await context.bot.get_file(document.file_id)
            unique_id = str(uuid.uuid4())
            docx_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.{file_extension}")
            pdf_filename = f"{unique_id}.pdf"
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
            
            await file.download_to_drive(docx_path)
            
            success = await convert_word_to_pdf(docx_path, pdf_path)
            
            if success and os.path.exists(pdf_path):
                await status_message.edit_text("✅ Konvertatsiya muvaffaqiyatli!")
                
                with open(pdf_path, 'rb') as pdf_file:
                    await message.reply_document(
                        document=pdf_file,
                        filename=f"{os.path.splitext(document.file_name)[0]}.pdf",
                        caption="✅ Word PDF formatiga o'zgartirildi\n🌐 Soliq.uz",
                        reply_markup=create_convert_keyboard()
                    )
                context.user_data['convert_mode'] = None
            else:
                await status_message.edit_text(
                    "❌ Konvertatsiya xatoligi. Iltimos qaytadan urinib ko'ring.",
                    reply_markup=create_convert_keyboard()
                )
        except Exception as e:
            logger.error(f"Word to PDF handler xatoligi: {e}")
            await status_message.edit_text(
                f"❌ Xatolik yuz berdi: {str(e)}",
                reply_markup=create_convert_keyboard()
            )
        finally:
            if docx_path and os.path.exists(docx_path):
                os.remove(docx_path)
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)
        return
    
    elif convert_mode == 'add_qr_to_word':
        if file_extension != 'docx':
            await message.reply_text(
                "❌ Xatolik: Iltimos DOCX fayl yuboring!\n\n"
                "💡 Maslahat: Agar DOC faylingiz bo'lsa, uni birinchi DOCX ga o'zgartiring.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Orqaga", callback_data='back_to_main')]])
            )
            return
        
        status_message = await message.reply_text("⏳ Word faylga QR kod qo'shilmoqda...")
        
        original_docx_path = None
        qr_image_path = None
        output_docx_path = None
        try:
            file = await context.bot.get_file(document.file_id)
            unique_id = str(uuid.uuid4())
            original_docx_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_original.{file_extension}")
            output_docx_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_with_qr.docx")
            qr_image_path = os.path.join(QR_FOLDER, f"{unique_id}.png")
            
            # Download original file
            await file.download_to_drive(original_docx_path)
            
            # Create permanent file link and QR code
            permanent_filename = f"{uuid.uuid4()}.{file_extension}"
            permanent_file_path = os.path.join(UPLOAD_FOLDER, permanent_filename)
            file_url = f"{get_base_url()}/files/{permanent_filename}"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(file_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(qr_image_path)
            
            # Add QR code to Word document
            success = await add_qr_to_word_document(original_docx_path, qr_image_path, output_docx_path)
            
            if success and os.path.exists(output_docx_path):
                await status_message.edit_text("✅ QR kod muvaffaqiyatli qo'shildi!")
                
                # Save the file with QR code as the permanent file
                os.rename(output_docx_path, permanent_file_path)
                
                # Send document with QR code
                with open(permanent_file_path, 'rb') as docx_file:
                    await message.reply_document(
                        document=docx_file,
                        filename=f"{os.path.splitext(document.file_name)[0]}_QR.docx",
                        caption=f"✅ Word faylga QR kod qo'shildi!\n\n📥 Yuklab olish: {file_url}\n🌐 Soliq.uz",
                        reply_markup=create_main_keyboard()
                    )
                context.user_data['convert_mode'] = None
            else:
                await status_message.edit_text(
                    "❌ QR kod qo'shishda xatolik. Iltimos qaytadan urinib ko'ring.",
                    reply_markup=create_main_keyboard()
                )
        except Exception as e:
            logger.error(f"Word faylga QR qo'shish handler xatoligi: {e}")
            await status_message.edit_text(
                f"❌ Xatolik yuz berdi: {str(e)}",
                reply_markup=create_main_keyboard()
            )
        finally:
            if original_docx_path and os.path.exists(original_docx_path):
                os.remove(original_docx_path)
            if qr_image_path and os.path.exists(qr_image_path):
                os.remove(qr_image_path)
            if output_docx_path and os.path.exists(output_docx_path):
                os.remove(output_docx_path)
        return
    
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

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the bot"""
    logger.error(f"Xatolik yuz berdi: {context.error}")
    
    if isinstance(context.error, Conflict):
        logger.warning("Conflict xatoligi: Bir nechta bot nusxasi ishlayotgan bo'lishi mumkin")
        return
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Uzr, xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.",
                reply_markup=create_main_keyboard()
            )
    except Exception as e:
        logger.error(f"Xatolik xabarini yuborishda muammo: {e}")

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
    
    application.add_error_handler(error_handler)
    
    print("🤖 Bot ishga tushdi! Fayllarni qabul qilish uchun tayyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
