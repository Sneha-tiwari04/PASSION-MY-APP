import os
import json
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes, ConversationHandler
)

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Conversation Stages ---
NAME, AGE, QUALIFICATION, SELECTION, VISION_FEEDBACK = range(5)

# --- Helper Functions ---
def get_job_data(key):
    try:
        # Dhyan rahe data.json file isi folder mein ho
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f).get(key, {})
    except Exception as e:
        logger.error(f"Error reading JSON: {e}")
        return {}

async def send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(1.2)

# --- Conversation Logic ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing(update, context)
    await update.message.reply_text(
        "✨ *Hello! Kaise hain aap?*\n\n"
        "Main aapka *Career Guide* dost hoon. Aapke ujjwal bhavishya ki "
        "shubhkamnayein karte hue, main aapki har sambhav madad karne ke liye hazir hoon. 🛡️\n\n"
        "Chaliye shuru karte hain! Sabse pehle kripya apna *Pura Naam* batayein?",
        parse_mode=ParseMode.MARKDOWN
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 2 or any(char.isdigit() for char in name):
        await update.message.reply_text("Maafi chahta hoon, kripya apna sahi naam (sirf akshar) batayein. 😊")
        return NAME
    
    context.user_data['name'] = name
    await send_typing(update, context)
    await update.message.reply_text(f"Bahut sundar naam hai, *{name}*! ✨\n\nAb mujhe apni *Age* (Umar) batayein?", parse_mode=ParseMode.MARKDOWN)
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age_text = update.message.text.strip()
    if not age_text.isdigit() or not (12 <= int(age_text) <= 90):
        await update.message.reply_text("Kripya apni sahi umar sirf numbers mein batayein (12-60 ke beech).")
        return AGE
    
    context.user_data['age'] = age_text
    await send_typing(update, context)
    await update.message.reply_text("Shukriya! Ab apni *Highest Qualification* batayein (jaise 10th, 12th, ya Graduation)?", parse_mode=ParseMode.MARKDOWN)
    return QUALIFICATION

async def get_qualification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['qual'] = update.message.text.strip()
    await send_typing(update, context)
    
    keyboard = [
        [InlineKeyboardButton("🎓 10th Pass Options", callback_data='10th')],
        [InlineKeyboardButton("📜 12th Pass Options", callback_data='12th')],
        [InlineKeyboardButton("🏛️ Graduation & Above", callback_data='Graduation')]
    ]
    
    await update.message.reply_text(
        "Behtareen! Maine aapki jankari note kar li hai.\n\n"
        "Ab niche diye gaye buttons mein se apni category chunein:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )
    return SELECTION

async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Button click response ko acknowledge karna zaroori hai
    
    category = query.data
    info = get_job_data(category)
    name = context.user_data.get('name', 'Dost')

    if not info:
        await query.message.reply_text("Maafi chaahta hu, iske baare me mera data available nahi hai. 😔")
        return ConversationHandler.END

    await send_typing(update, context)

    # Photos bhejnah
    if "photos" in info:
        for p_url in info["photos"]:
            if p_url and "image.png" not in p_url: # Sirf valid links ke liye
                try:
                    await context.bot.send_photo(chat_id=query.message.chat_id, photo=p_url)
                except:
                    continue

    links_text = "".join([f"🔹 [{l['name']}]({l['url']})\n" for l in info.get('links', [])])
    
    response = (
        f"🚀 *Career Roadmap for {name}* 🚀\n\n"
        f"💼 *Job Links:*\n{links_text if links_text else 'Nayi updates jald aayengi...'}\n"
        f"🛤️ *Roadmap:* {info.get('roadmap', 'Updating...')}\n\n"
        f"💡 *Mantra:* _{info.get('motivation', 'Mehnat kabhi bekar nahi jati.')}_"
    )
    await query.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    # Vision Question
    await asyncio.sleep(1)
    vision_text = (
        f"🙏 *{name}, ek intelligent insan ke taur par aapki rai chahiye...*\n\n"
        "Hum ek aisa **Advanced Software** la rahe hain jahan aapko websites dhundne ki "
        "zarurat nahi hogi. AI ke zariye aapke forms khud bhare jayenge. Kya aapko lagta hai "
        "ki ye India ke liye useful rahega?"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Haan, Bilkul Useful!", callback_data='v_yes')],
        [InlineKeyboardButton("❌ Nahi, Iski Zarurat Nahi", callback_data='v_no')]
    ]
    await query.message.reply_text(vision_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    return VISION_FEEDBACK

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    opinion = "YES (Useful)" if query.data == 'v_yes' else "NO (Not Useful)"
    logger.info(f"FEEDBACK: User {query.from_user.full_name} said {opinion}")

    msg = "✅ *Aapne 'YES' chuna hai. Shukriya!*" if query.data == 'v_yes' else "Shukriya aapki rai ke liye."

    keyboard = [
        [InlineKeyboardButton("🗑️ Mera Data Delete Karein", callback_data='delete_data')],
        [InlineKeyboardButton("👋 Theek hai, Alvida!", callback_data='just_exit')]
    ]
    
    await query.edit_message_text(
        f"{msg}\n\nKya aap chahte hain ki main aapka data system se delete kar dun?\n"
        "*(Aapka suggestion hamare paas surakshit rahega)*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )
    return VISION_FEEDBACK

async def handle_final_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'delete_data':
        context.user_data.clear()
        final_text = "✅ *Aapka personal data delete kar diya gaya hai.*"
    else:
        final_text = "Aapka data surakshit hai."

    await query.edit_message_text(
        f"{final_text}\n\nAapka din mangalmay ho. ✨\n\n(Dobara shuru karne ke liye /start likhein)"
    )
    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Maafi chaahta hu, iske baare me mera data available nahi hai. 😔")

async def error_handler(update, context):
    logger.error(f"Error: {context.error}")

# --- Main Function ---
def main():
    TOKEN = "8549362510:AAFBmENG89fMjUM27lF2BfJ7rPtrmKMzXxY"
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex('^(Hi|hi|Hii|hii|Hello|hello)$'), start)
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            QUALIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_qualification)],
            SELECTION: [CallbackQueryHandler(handle_selection)],
            VISION_FEEDBACK: [
                CallbackQueryHandler(handle_final_action, pattern='^(delete_data|just_exit)$'),
                CallbackQueryHandler(handle_feedback, pattern='^v_')
            ],
        },
        fallbacks=[CommandHandler('start', start), MessageHandler(filters.ALL, unknown)],
        per_message=False # <--- Sabse important fix
    )

    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)

    print("✅ Bot is fixed and running!")
    app.run_polling()

if __name__ == '__main__':
    main()