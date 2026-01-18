import telebot
import requests

# 1. Apna Token yahan daalo
API_TOKEN = '8549362510:AAFBmENG89fMjUM27lF2BfJ7rPtrmKMzXxY' # Yahan apna sahi token paste karna
bot = telebot.TeleBot(API_TOKEN)

# 2. Tumhara Sahi GitHub RAW Link
DATA_URL = ""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 Passion Job Bot Active hai!\nType /jobs latest updates dekhne ke liye.")

@bot.message_handler(commands=['jobs'])
def show_jobs(message):
    try:
        response = requests.get(DATA_URL)
        if response.status_code == 200:
            jobs = response.json()
            if not jobs:
                bot.send_message(message.chat.id, "📭 Abhi koi jobs nahi hain. GitHub Action check karein.")
                return

            msg = "🔥 **Latest Jobs for You** 🔥\n\n"
            for job in jobs[:10]:
                msg += f"📌 {job['title']}\n🔗 [Apply]({job['link']})\n\n"
            
            bot.send_message(message.chat.id, msg, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            bot.send_message(message.chat.id, "❌ GitHub se data nahi mil raha. Permission check karein.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

print("🤖 Bot chalu hai...")
bot.infinity_polling()