import logging
import sqlite3
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8075140211:AAGKH8iipiCBhvjjKw9JexYhe9aCNoYhgFs"

# دیتابیس
conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT, join_date TEXT)''')
conn.commit()

# منوی اصلی
main_menu = ReplyKeyboardMarkup([
    ["صفحه اصلی"], ["پروفایل من"],
    ["راهنما"], ["آمار ربات"], ["پشتیبانی"]
], resize_keyboard=True)

inline_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("ویرایش پروفایل", callback_data="edit")],
    [InlineKeyboardButton("خروج", callback_data="exit")]
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)",
                   (user.id, user.first_name, user.username, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    await update.message.reply_text(
        f"سلام {user.first_name} عزیز!\nبه ربات رفرال خوش اومدی 🎉\n\nاز منوی پایین استفاده کن:",
        reply_markup=main_menu
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "صفحه اصلی":
        await update.message.reply_text("صفحه اصلی 🏠", reply_markup=main_menu)
    elif text == "پروفایل من":
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        u = cursor.fetchone()
        await update.message.reply_text(
            f"پروفایل شما:\n\n🆔 آیدی: {u[0]}\n👤 نام: {u[1]}\n📛 یوزرنیم: @{u[2] or 'ندارد'}\n📅 تاریخ جوین: {u[3]}",
            reply_markup=inline_menu
        )
    elif text == "راهنما":
        await update.message.reply_text("این ربات فقط تست هست. بعداً رفرال و جایزه اضافه می‌کنیم 😊")
    elif text == "آمار ربات":
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        await update.message.reply_text(f"تعداد کاربران تا الان: {count} نفر")
    elif text == "پشتیبانی":
        await update.message.reply_text("پشتیبانی: @alip1389")
    else:
        await update.message.reply_text("از منو استفاده کن!", reply_markup=main_menu)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "exit":
        await query.message.reply_text("خروج کردی!", reply_markup=main_menu)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
app.add_handler(CallbackQueryHandler(callback_handler))

print("ربات در حال اجراست...")
app.run_polling()
