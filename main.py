import os
import re
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

INSTAGRAM_REGEX = re.compile(r"(https?://)?(www\.)?(instagram\.com)/.+")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom!\n\n"
        "Men sizga Instagram videoni audio formatga aylantirib beraman 🎧\n\n"
        "Instagram link yuboring."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not INSTAGRAM_REGEX.match(text):
        await update.message.reply_text("❌ Bu Instagram link emas.")
        return

    await update.message.reply_text("🎵 Link qabul qilindi\n⚡ Audio tayyorlanmoqda...")

    output = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "--no-playlist",
        "--no-part",
        "--no-mtime",
        "--no-check-certificate",
        "--add-header", "User-Agent:Mozilla/5.0",
        "-o", output,
        text
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.communicate()

        files = os.listdir(DOWNLOAD_DIR)
        if not files:
            raise Exception("Audio topilmadi")

        path = os.path.join(DOWNLOAD_DIR, files[0])

        await update.message.reply_audio(
            audio=open(path, "rb"),
            caption="🎧 Tayyor!"
        )

        os.remove(path)

    except Exception:
        await update.message.reply_text(
            "❌ Xatolik yuz berdi.\n"
            "Iltimos, boshqa public video bilan urinib ko‘ring."
        )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Instagram Audio Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
