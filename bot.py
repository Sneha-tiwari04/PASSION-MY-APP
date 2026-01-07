import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8549362510:AAFBmENG89fMjUM27lF2BfJ7rPtrmKMzXxY"

# Load jobs
def load_jobs():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

jobs = load_jobs()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Hello user 👋\n"
        "Sukriya, aap bilkul sahi jagah ho 😊\n\n"
        "Sabse pehle apna *naam* batayein:",
        parse_mode="Markdown"
    )
    context.user_data["state"] = "name"

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    state = context.user_data.get("state")

    if state == "name":
        context.user_data["name"] = text
        await update.message.reply_text("Apni *age* batayein:")
        context.user_data["state"] = "age"

    elif state == "age":
        if not text.isdigit():
            await update.message.reply_text("Please sahi age number me likhein.")
            return
        context.user_data["age"] = text
        await update.message.reply_text("Qualification batayein (10th / 12th):")
        context.user_data["state"] = "qualification"

    elif state == "qualification":
        q = text.lower()
        if q not in ["10th", "12th"]:
            await update.message.reply_text("Sirf 10th ya 12th likhein.")
            return

        matched = [j for j in jobs if j["qualification"] == q]

        if not matched:
            await update.message.reply_text("Abhi is qualification ke liye vacancy nahi hai.")
        else:
            msg = "Aapke liye available govt vacancies 👇\n\n"
            for j in matched:
                msg += f"🔹 {j['title']}\n🔗 {j['link']}\n\n"
            await update.message.reply_text(msg)

        await update.message.reply_text(
            "📌 Chhoti si guidance:\n"
            "• Roz official websites check karein\n"
            "• Form bharte time details dhyaan se bharein\n"
            "• Kisi dalal se door rahein\n"
            "• Mehnat aur patience rakhein\n\n"
            "Thank you 🙏 Best of luck 🌸"
        )
        context.user_data.clear()

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()