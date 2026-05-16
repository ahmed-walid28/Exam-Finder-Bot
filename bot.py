"""
Exam Information Bot
Telegram bot for exam information lookup
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


def get_subject_display_name(subject_key):
    """Return the clean subject name for display."""
    return SUBJECT_DISPLAY_NAMES.get(subject_key, subject_key)


def build_subject_keyboard():
    """Build the subject selection keyboard."""
    buttons = []
    for i, subject in enumerate(SUBJECTS_LIST):
        display_name = get_subject_display_name(subject)
        buttons.append([
            InlineKeyboardButton(display_name, callback_data=f"subject_{i}")
        ])

    return InlineKeyboardMarkup(buttons)


def build_navigation_keyboard(include_search_again=False):
    """Build a small navigation keyboard for the result screens."""
    buttons = []
    if include_search_again:
        buttons.append([InlineKeyboardButton("New search", callback_data="search_again")])

    buttons.append([InlineKeyboardButton("Main menu", callback_data="home")])

    return InlineKeyboardMarkup(buttons)

async def update_callback_message(query, text, reply_markup, parse_mode="HTML"):
    """Edit the callback message text."""
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )


def main_menu_text():
    return (
        "<b>Welcome to the Exam Information Bot</b>\n\n"
        "Choose a subject from the list below:"
    )


def subject_prompt_text(display_name):
    return (
        f"<b>📘 {display_name}</b>\n\n"
        "Enter the student ID to continue:"
    )


def format_exam_result(student_id, display_subject_name, student_info):
    """Format the success response as a cleaner card-like message."""
    return (
        "<b>✨ Exam Details</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📚 <b>Subject</b>\n{display_subject_name}\n\n"
        f"👤 <b>Student name</b>\n{student_info['name']}\n\n"
        f"🆔 <b>Student ID</b>\n<code>{student_id}</code>\n\n"
        f"📍 <b>Exam location</b>\n{student_info['location']}\n\n"
        f"🕒 <b>Time</b>\n{student_info['time']}"
    )


def format_no_result_message(student_id, display_subject_name):
    """Format the failure response with a cleaner layout."""
    return (
        "<b>🔎 No data found</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📚 Subject: {display_subject_name}\n"
        f"🆔 Student ID: <code>{student_id}</code>\n\n"
        "Check the ID and try again."
    )


def extract_subject_name(filename):
    """Extract a clean subject name from the filename."""
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
                print(f"Loaded: {clean_display_name} ({len(students_data)} students)")
        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    SUBJECTS_LIST.sort(key=lambda subject: get_subject_display_name(subject).casefold())
    print(f"\nSuccessfully loaded {len(SUBJECTS)} subjects\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command - show subjects"""
    if not SUBJECTS:
        await update.message.reply_text(
            "No data is available. Make sure the data files exist in the Data folder"
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        main_menu_text(),
        reply_markup=build_subject_keyboard(),
        parse_mode="HTML"
    )
    
    return SELECTING_SUBJECT


async def subject_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle subject selection"""
    query = update.callback_query
    await query.answer()
    
    subject_idx = int(query.data.split("_")[1])
    selected_subject = SUBJECTS_LIST[subject_idx]
    display_name = get_subject_display_name(selected_subject)
    
    # Store selected subject in context
    context.user_data['selected_subject'] = selected_subject
    
    await query.edit_message_text(
        subject_prompt_text(display_name),
        reply_markup=build_navigation_keyboard(),
        parse_mode="HTML"
    )
    
    return ENTERING_ID


async def process_student_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process student ID and return exam info"""
    student_id = update.message.text.strip()
    selected_subject = context.user_data.get('selected_subject')
    display_subject_name = get_subject_display_name(selected_subject)
    
    if not selected_subject:
        await update.message.reply_text("No subject was selected. Send /start to begin.")
        return ConversationHandler.END
    
    # Search for student in the selected subject
    students_data = SUBJECTS[selected_subject]
    
    if student_id in students_data:
        student_info = students_data[student_id]
        response = format_exam_result(student_id, display_subject_name, student_info)
    else:
        response = format_no_result_message(student_id, display_subject_name)
    
    # Add option to search again
    await update.message.reply_text(
        response,
        reply_markup=build_navigation_keyboard(include_search_again=True),
        parse_mode="HTML"
    )
    
    return ENTERING_ID


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle callback buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "search_again":
        selected_subject = context.user_data.get('selected_subject')
        if not selected_subject:
            context.user_data.clear()
            await update_callback_message(
                query,
                main_menu_text(),
                build_subject_keyboard(),
                parse_mode="HTML"
            )
            return SELECTING_SUBJECT

        display_name = get_subject_display_name(selected_subject)
        await update_callback_message(
            query,
            subject_prompt_text(display_name),
            build_navigation_keyboard(),
            parse_mode="HTML"
        )
        return ENTERING_ID
    
    elif query.data == "home":
        context.user_data.clear()
        await update_callback_message(
            query,
            main_menu_text(),
            build_subject_keyboard(),
            parse_mode="HTML"
        )
        return SELECTING_SUBJECT


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = """<b>Usage Instructions</b>

<b>Steps:</b>
1. Send /start to begin
2. Choose a subject from the list
3. Enter your student ID
4. You will get the exam details immediately

<b>Important notes:</b>
- The ID should contain numbers only (example: 4221006)
- If the ID is not found, you may not be registered in this subject
- You can search across multiple subjects one after another

<b>To start:</b> send /start"""
    await update.message.reply_text(help_text, parse_mode="HTML")


def main():
    """Start the bot"""
    # Load exam data
    load_data()
    
    if not SUBJECTS:
        print("No data was loaded. Make sure the data files exist in the Data folder")
        return
    
    # Load environment variables
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        print("BOT_TOKEN was not found")
        print("Set the BOT_TOKEN environment variable or create a .env file")
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
    application.add_handler(CallbackQueryHandler(handle_callback, pattern="^(search_again|home)$"))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    
    # Run the bot
    print("Bot is running... (press Ctrl+C to stop)")
    application.run_polling()


if __name__ == "__main__":
    main()
