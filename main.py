
import os
import logging
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SHEET_NAME = "Tasks"
SPREADSHEET_URL = os.environ.get("SPREADSHEET_URL")

# === ДОСТУП К GOOGLE SHEETS ===
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open_by_url(SPREADSHEET_URL).worksheet(SHEET_NAME)

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)

# === ОБРАБОТКА СООБЩЕНИЙ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user.first_name

    row = [""] * 18
    row[3] = text  # Task
    row[4] = "One-time"
    row[6] = user  # Responsible
    row[15] = "10:00"
    row[16] = 2
    row[17] = "Every Monday"

    sheet.append_row(row)
    await update.message.reply_text(f"✅ Задача добавлена: «{text}»")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши задачу в свободной форме, и я добавлю её в таблицу 📋")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
