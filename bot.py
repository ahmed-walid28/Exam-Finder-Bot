"""
Exam Information Bot
بوت تليجرام للحصول على معلومات الامتحانات
"""

import os
import sys
import csv
import re
from pathlib import Path
from dotenv import load_dotenv

# Fix Unicode encoding for Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# States for conversation
SELECTING_SUBJECT, ENTERING_ID = range(2)

# Data directory path
DATA_DIR = Path(__file__).parent / "Data"

# Store subjects and data
SUBJECTS = {}
SUBJECTS_LIST = []
SUBJECT_DISPLAY_NAMES = {}  # Store clean display names


def extract_subject_name(filename):
    """استخراج اسم المادة النظيف من اسم الملف"""
    # Remove file number like {12}, {15}, etc.
    clean = re.sub(r'^\{\d+\}\s*-\s*', '', filename)
    # Remove date patterns: - 8-6-2026 or - (18-5-2026)
    clean = re.sub(r'\s*-\s*\(\d{1,2}-\d{1,2}-\d{4}\).*$', '', clean)
    clean = re.sub(r'\s*-\s*\d{1,2}-\d{1,2}-\d{4}.*$', '', clean)
    # Remove outer parentheses
    clean = re.sub(r'^\s*\(', '', clean)
    clean = re.sub(r'\)\s*$', '', clean)
    return clean.strip()


def load_data():
    """Load all exam data from CSV files"""
    global SUBJECTS, SUBJECTS_LIST, SUBJECT_DISPLAY_NAMES
    
    if not DATA_DIR.exists():
        print(f"Error: Data directory not found: {DATA_DIR}")
        return
    
    # Read all text files in Data directory
    for file_path in DATA_DIR.glob("*.txt"):
        try:
            subject_name = file_path.stem  # Get filename without extension
            clean_display_name = extract_subject_name(subject_name)
            students_data = {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row and 'كود الطالب' in row:
                        student_id = row['كود الطالب'].strip()
                        students_data[student_id] = {
                            'name': row.get('اسم الطالب', ''),
                            'location': row.get('مكان الامتحان', ''),
                            'time': row.get('الوقت', '')
                        }
            
            if students_data:
                SUBJECTS[subject_name] = students_data
                SUBJECTS_LIST.append(subject_name)
                SUBJECT_DISPLAY_NAMES[subject_name] = clean_display_name
                print(f"✓ تم تحميل: {clean_display_name} ({len(students_data)} طالب)")
        
        except Exception as e:
            print(f"✗ خطأ في قراءة {file_path}: {e}")
    
    SUBJECTS_LIST.sort()
    print(f"\nتم تحميل {len(SUBJECTS)} مادة بنجاح\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command - show subjects"""
    if not SUBJECTS:
        await update.message.reply_text(
            "❌ لا توجد بيانات متاحة. تأكد من وجود ملفات البيانات في مجلد Data"
        )
        return ConversationHandler.END
    
    # Create inline buttons for subjects with clean names
    buttons = []
    for i, subject in enumerate(SUBJECTS_LIST, 1):
        display_name = SUBJECT_DISPLAY_NAMES.get(subject, subject)
        buttons.append([InlineKeyboardButton(
            f"📚 {display_name}",
            callback_data=f"subject_{i-1}"
        )])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(
        "🎓 <b>مرحباً في بوت معلومات الامتحانات!</b>\n\n"
        "📍 اختر المادة:\n",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    
    return SELECTING_SUBJECT


async def subject_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle subject selection"""
    query = update.callback_query
    await query.answer()
    
    subject_idx = int(query.data.split("_")[1])
    selected_subject = SUBJECTS_LIST[subject_idx]
    display_name = SUBJECT_DISPLAY_NAMES.get(selected_subject, selected_subject)
    
    # Store selected subject in context
    context.user_data['selected_subject'] = selected_subject
    
    await query.edit_message_text(
        f"✅ <b>{display_name}</b>\n\n"
        f"🔢 أدخل كود الطالب:",
        parse_mode="HTML"
    )
    
    return ENTERING_ID


async def process_student_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process student ID and return exam info"""
    student_id = update.message.text.strip()
    selected_subject = context.user_data.get('selected_subject')
    display_subject_name = SUBJECT_DISPLAY_NAMES.get(selected_subject, selected_subject)
    
    if not selected_subject:
        await update.message.reply_text("❌ خطأ: لم يتم اختيار مادة. اكتب /start للبدء")
        return ConversationHandler.END
    
    # Search for student in the selected subject
    students_data = SUBJECTS[selected_subject]
    
    if student_id in students_data:
        student_info = students_data[student_id]
        response = (
            f"<b>✅ تم العثور على البيانات!</b>\n\n"
            f"📚 <b>المادة:</b>\n{display_subject_name}\n\n"
            f"👤 <b>الاسم:</b>\n{student_info['name']}\n\n"
            f"🆔 <b>الكود:</b> {student_id}\n\n"
            f"📍 <b>مكان الامتحان:</b>\n{student_info['location']}\n\n"
            f"🕐 <b>الوقت:</b>\n{student_info['time']}"
        )
    else:
        response = (
            f"❌ <b>لم يتم العثور على البيانات</b>\n\n"
            f"❌ كود الطالب: <code>{student_id}</code>\n"
            f"📚 المادة: {display_subject_name}\n\n"
            f"💡 تحقق من الكود وحاول مرة أخرى"
        )
    
    # Add option to search again
    buttons = [[
        InlineKeyboardButton("🔍 بحث جديد", callback_data="search_again"),
        InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="home")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="HTML")
    
    return ConversationHandler.END


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle callback buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "search_again":
        # Reset and start over
        context.user_data.clear()
        return await start(query, context)
    
    elif query.data == "home":
        # Go back to subject selection
        context.user_data.clear()
        return await start(query, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = """<b>🆘 تعليمات الاستخدام:</b>

<b>خطوات الاستخدام:</b>
1️⃣ اضغط /start لبدء البوت
2️⃣ اختر المادة من القائمة 📚
3️⃣ أدخل كود الطالب الخاص بك
4️⃣ ستحصل على معلومات الامتحان فوراً ✅

<b>ℹ️ معلومات مهمة:</b>
• الكود يكون أرقام فقط (مثال: 4221006)
• إذا لم يظهر الكود، فقد لا تكون مسجل بهذه المادة
• يمكنك البحث في عدة مواد بالتتابع

<b>📞 للبدء:</b> اكتب /start 🚀"""
    await update.message.reply_text(help_text, parse_mode="HTML")


def main():
    """Start the bot"""
    # Load exam data
    load_data()
    
    if not SUBJECTS:
        print("❌ لم يتم تحميل أي بيانات. تأكد من وجود ملفات البيانات في مجلد Data")
        return
    
    # Load environment variables
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        print("❌ لم يتم العثور على BOT_TOKEN")
        print("يرجى تعيين متغير البيئة BOT_TOKEN أو إنشاء ملف .env")
        return
    
    # Create the Application
    application = Application.builder().token(bot_token).build()
    
    # Set up conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_SUBJECT: [
                CallbackQueryHandler(subject_selected, pattern="^subject_")
            ],
            ENTERING_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_student_id),
                CallbackQueryHandler(handle_callback, pattern="^(search_again|home)$")
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CallbackQueryHandler(handle_callback, pattern="^(search_again|home)$")
        ],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    
    # Run the bot
    print("🤖 البوت يعمل الآن... (اضغط Ctrl+C للإيقاف)")
    application.run_polling()


if __name__ == "__main__":
    main()
