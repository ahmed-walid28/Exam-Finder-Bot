"""
Exam Information Bot
بوت تليجرام للحصول على معلومات الامتحانات
"""

import os
import csv
from pathlib import Path
from dotenv import load_dotenv
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


def load_data():
    """Load all exam data from CSV files"""
    global SUBJECTS, SUBJECTS_LIST
    
    if not DATA_DIR.exists():
        print(f"Error: Data directory not found: {DATA_DIR}")
        return
    
    # Read all text files in Data directory
    for file_path in DATA_DIR.glob("*.txt"):
        try:
            subject_name = file_path.stem  # Get filename without extension
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
                print(f"✓ تم تحميل: {subject_name} ({len(students_data)} طالب)")
        
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
    
    # Create inline buttons for subjects
    buttons = []
    for i, subject in enumerate(SUBJECTS_LIST, 1):
        buttons.append([InlineKeyboardButton(
            f"{i}. {subject}",
            callback_data=f"subject_{i-1}"
        )])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(
        "🎓 مرحباً في بوت معلومات الامتحانات!\n\n"
        "اختر المادة التي تريد معرفة معلومات امتحانك فيها:\n",
        reply_markup=reply_markup
    )
    
    return SELECTING_SUBJECT


async def subject_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle subject selection"""
    query = update.callback_query
    await query.answer()
    
    subject_idx = int(query.data.split("_")[1])
    selected_subject = SUBJECTS_LIST[subject_idx]
    
    # Store selected subject in context
    context.user_data['selected_subject'] = selected_subject
    
    await query.edit_message_text(
        f"✅ تم اختيار: {selected_subject}\n\n"
        f"📝 الآن أدخل كود الطالب (Student ID):"
    )
    
    return ENTERING_ID


async def process_student_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process student ID and return exam info"""
    student_id = update.message.text.strip()
    selected_subject = context.user_data.get('selected_subject')
    
    if not selected_subject:
        await update.message.reply_text("❌ خطأ: لم يتم اختيار مادة. اكتب /start للبدء")
        return ConversationHandler.END
    
    # Search for student in the selected subject
    students_data = SUBJECTS[selected_subject]
    
    if student_id in students_data:
        student_info = students_data[student_id]
        response = (
            f"✅ تم العثور على البيانات!\n\n"
            f"📚 المادة: {selected_subject}\n"
            f"👤 اسم الطالب: {student_info['name']}\n"
            f"🆔 كود الطالب: {student_id}\n"
            f"📍 مكان الامتحان: {student_info['location']}\n"
            f"🕐 الوقت: {student_info['time']}\n"
        )
    else:
        response = (
            f"❌ لم يتم العثور على كود الطالب: {student_id}\n"
            f"في المادة: {selected_subject}\n\n"
            f"تحقق من الكود وحاول مرة أخرى."
        )
    
    # Add option to search again
    buttons = [[
        InlineKeyboardButton("🔍 بحث آخر", callback_data="search_again"),
        InlineKeyboardButton("🏠 الرئيسية", callback_data="home")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(response, reply_markup=reply_markup)
    
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
    help_text = """
🆘 تعليمات الاستخدام:

1️⃣ اكتب /start لبدء البوت
2️⃣ اختر المادة من القائمة
3️⃣ أدخل كود الطالب (4-digit Student ID)
4️⃣ سيظهر لك مكان الامتحان والوقت

📝 ملاحظات:
• تأكد من كتابة الكود بشكل صحيح
• الكود يكون بصيغة رقمية (مثال: 4221006)
• يمكنك البحث عن عدة مواد بالتتابع

اكتب /start للبدء 🚀
    """
    await update.message.reply_text(help_text)


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
