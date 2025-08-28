import os
import json
import logging
import gspread
from google.oauth2 import service_account
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === DEBUG: показать все переменные окружения в Railway ===
print("DEBUG VARS:", dict(os.environ))

# === Настройки ===
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Обязательно добавь эти переменные в Railway (.env):
SPREADSHEET_URL = os.environ["SPREADSHEET_URL"]
SHEET_NAME = os.environ["SHEET_NAME"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

# === Авторизация Google Sheets через переменные Railway ===
service_account_info = {
    "type": os.environ["GOOGLE_TYPE"],
    "project_id": os.environ["GOOGLE_PROJECT_ID"],
    "private_key_id": os.environ["GOOGLE_PRIVATE_KEY_ID"],
    "private_key": os.environ["GOOGLE_PRIVATE_KEY"].replace("\\n", "\n"),
    "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
    "client_id": os.environ["GOOGLE_CLIENT_ID"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.environ['GOOGLE_CLIENT_EMAIL'].replace('@', '%40')}"
}

creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
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