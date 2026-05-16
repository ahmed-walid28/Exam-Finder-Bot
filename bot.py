"""
Exam Information Bot
Telegram bot for exam information lookup
"""

import os
import sys
import csv
import re
from io import BytesIO
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

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    Image = ImageDraw = ImageFilter = ImageFont = None


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


def load_font(size, bold=False):
    """Load a readable font with safe fallbacks."""
    if ImageFont is None:
        return None

    candidates = []
    if bold:
        candidates.extend([
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\seguiemj.ttf",
        ])
    else:
        candidates.extend([
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
        ])

    candidates.extend([
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ])

    for font_path in candidates:
        if Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception:
                continue

    return ImageFont.load_default()


def create_exam_card_image(student_id, display_subject_name, student_info):
    """Create a modern exam details card image."""
    if Image is None:
        return None

    width = height = 1200
    background = Image.new("RGBA", (width, height), (10, 14, 35, 255))
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Soft gradient background layers.
    for y in range(height):
        ratio = y / max(1, height - 1)
        r = int(12 + (30 - 12) * ratio)
        g = int(18 + (10 - 18) * ratio)
        b = int(45 + (85 - 45) * ratio)
        overlay_draw.line((0, y, width, y), fill=(r, g, b, 255))

    background = Image.alpha_composite(background, overlay)

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((-120, -60, 540, 520), fill=(70, 120, 255, 90))
    glow_draw.ellipse((700, 60, 1260, 620), fill=(155, 90, 255, 75))
    glow_draw.ellipse((360, 760, 1020, 1320), fill=(45, 180, 255, 50))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    background = Image.alpha_composite(background, glow)

    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((155, 175, 1045, 985), radius=48, fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(35))
    background = Image.alpha_composite(background, shadow)

    base = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    base.paste(background, (0, 0))

    card_x1, card_y1 = 170, 185
    card_x2, card_y2 = 1030, 975
    card_draw = ImageDraw.Draw(base)
    card_draw.rounded_rectangle((card_x1, card_y1, card_x2, card_y2), radius=44, fill=(255, 255, 255, 28), outline=(255, 255, 255, 58), width=2)

    # Accent strips.
    card_draw.rounded_rectangle((card_x1 + 22, card_y1 + 22, card_x2 - 22, card_y1 + 32), radius=8, fill=(100, 150, 255, 210))
    card_draw.rounded_rectangle((card_x1 + 22, card_y2 - 32, card_x2 - 22, card_y2 - 22), radius=8, fill=(170, 100, 255, 170))

    title_font = load_font(58, bold=True)
    subtitle_font = load_font(28, bold=False)
    label_font = load_font(30, bold=True)
    value_font = load_font(34, bold=False)

    def text_size(draw, text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    header_y = 260
    title = "Exam Details"
    tw, th = text_size(card_draw, title, title_font)
    card_draw.text(((width - tw) / 2, header_y), title, font=title_font, fill=(255, 255, 255, 245))

    glow_text = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_text_draw = ImageDraw.Draw(glow_text)
    glow_text_draw.text(((width - tw) / 2, header_y), title, font=title_font, fill=(110, 170, 255, 85))
    glow_text = glow_text.filter(ImageFilter.GaussianBlur(10))
    base = Image.alpha_composite(base, glow_text)
    card_draw = ImageDraw.Draw(base)
    card_draw.text(((width - tw) / 2, header_y), title, font=title_font, fill=(255, 255, 255, 245))

    line_y = 350
    card_draw.line((330, line_y, 870, line_y), fill=(255, 255, 255, 80), width=2)

    icon_x = 290
    value_x = 410
    row_y = 410
    row_gap = 88
    fields = [
        ("📚", "Subject", display_subject_name),
        ("👤", "Student Name", student_info['name']),
        ("🪪", "Student ID", student_id),
        ("📍", "Location", student_info['location']),
        ("🕒", "Time", student_info['time']),
    ]

    for index, (icon, label, value) in enumerate(fields):
        y = row_y + index * row_gap
        pill_y1 = y - 12
        pill_y2 = y + 42
        card_draw.rounded_rectangle((card_x1 + 78, pill_y1, card_x2 - 78, pill_y2), radius=20, fill=(255, 255, 255, 14))
        card_draw.text((icon_x, y), icon, font=label_font, fill=(240, 245, 255, 245))
        card_draw.text((value_x, y - 2), f"{label}", font=subtitle_font, fill=(170, 185, 215, 255))
        card_draw.text((value_x, y + 28), str(value), font=value_font, fill=(255, 255, 255, 245))

    footer_font = load_font(22, bold=False)
    footer_text = "Verify the ID and keep this card for reference."
    fw, _ = text_size(card_draw, footer_text, footer_font)
    card_draw.text(((width - fw) / 2, 920), footer_text, font=footer_font, fill=(205, 215, 235, 170))

    output = BytesIO()
    base = base.convert("RGB")
    base.save(output, format="JPEG", quality=96, optimize=True)
    output.seek(0)
    output.name = "exam_details.jpg"
    return output


async def update_callback_message(query, text, reply_markup, parse_mode="HTML"):
    """Edit either the message text or the photo caption depending on message type."""
    if query.message and query.message.photo:
        await query.edit_message_caption(
            caption=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    else:
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
        "<b>✨ Exam details</b>\n"
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
        photo = create_exam_card_image(student_id, display_subject_name, student_info)
        if photo is None:
            response = format_exam_result(student_id, display_subject_name, student_info)
            await update.message.reply_text(
                response,
                reply_markup=build_navigation_keyboard(include_search_again=True),
                parse_mode="HTML"
            )
            return ENTERING_ID

        await update.message.reply_photo(
            photo=photo,
            caption="<b>Exam details</b>\n\nUse the buttons below to search again or return to the main menu.",
            reply_markup=build_navigation_keyboard(include_search_again=True),
            parse_mode="HTML"
        )
        return ENTERING_ID
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
