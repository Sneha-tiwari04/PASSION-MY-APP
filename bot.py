
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes, ConversationHandler
)

# Logging for Errors
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)



# States
NAME, AGE, EDUCATION, STREAM, HELP_REQUEST, FEEDBACK = range(6)

# JSON Loader
def get_data(key):
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            return data.get(key, {})
    except Exception as e:
        logger.error(f"JSON Load Error: {e}")
        return {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Hii! Main aapka dost...*\n\nAap ek *shant aur surakshit jagah* hain. Umeed hai main aapki madad kar pau. 😊\n\nSabse pehle, aap apna *Naam* btaein?",
        parse_mode=ParseMode.MARKDOWN
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"Badiya! Ab apni *Age* (Umar) btaein?")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("🎓 10th Pass", callback_data='10th')],
        [InlineKeyboardButton("📜 12th Pass", callback_data='12th')],
        [InlineKeyboardButton("🏛️ Graduate", callback_data='Graduation')]
    ]
    await update.message.reply_text("Apni *Education* select karein:", 
                                   reply_markup=InlineKeyboardMarkup(keyboard),
                                   parse_mode=ParseMode.MARKDOWN)
    return EDUCATION

async def handle_edu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    edu = query.data
    
    if edu == '10th':
        info = get_data('10th')
        text = (f"🌟 *10th Pass ke liye sunhare avasar:*\n\n🔗 *Job Links & Vacancy:*\n{info.get('vacancies')}\n\n"
                f"🛤️ *Roadmap:* {info.get('roadmap')}\n\n{info.get('motivation')}")
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
        return await ask_help_permission(update, context)
    
    elif edu == '12th':
        keyboard = [[InlineKeyboardButton("📐 Maths", callback_data='12th_Maths')],
                    [InlineKeyboardButton("🧬 Bio", callback_data='12th_Bio')],
                    [InlineKeyboardButton("🎨 Arts/Commerce", callback_data='12th_Arts')]]
        await query.edit_message_text("Aapka 12th mein kaun sa stream tha?", reply_markup=InlineKeyboardMarkup(keyboard))
        return STREAM

async def handle_stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    info = get_data(query.data)
    text = (f"🚀 *Career Roadmap & Vacancies:*\n\n{info.get('vacancies')}\n\n"
            f"🛣️ *Aage ka Rasta:* {info.get('roadmap')}\n\n{info.get('motivation')}")
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
    return await ask_help_permission(update, context)

async def ask_help_permission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.callback_query.message if update.callback_query else update.message
    keyboard = [[InlineKeyboardButton("Haan", callback_data='yes'), InlineKeyboardButton("Nahi", callback_data='no')]]
    await msg.reply_text("\n---\n🙏 *Mujhe aapki ek madad chahiye... Kya aap madad karenge?*", reply_markup=InlineKeyboardMarkup(keyboard))
    return HELP_REQUEST

async def show_vision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'no':
        await query.edit_message_text("Koi baat nahi! All the best aapke bhavishya ke liye. ❤️")
        return ConversationHandler.END

    vision_text = (
        "💡 *Hamara Vision:*\n\nHam ek aisa software banana chahte hain jisme aapke liye har tarah ki vacancy aur dheron sunhare avasar rahenge. "
        "Ab berojgari India mein nahi rahegi! *Passion* se berojgari door nahi, bahut door jayegi. 🚀\n\n"
        "Ham isme AI ke through official data aur Gov vacancy ko seedha aap tak pahonchayenge.\n\n"
        "*Aapko kya lagta hai, kya iski zarurat hai India mein?*"
    )
    keyboard = [
        [InlineKeyboardButton("1. Haan, bahut pehle se hai, jaldi lao!", callback_data='opt1')],
        [InlineKeyboardButton("2. Isme update karo abhi kafi kuch.", callback_data='opt2')],
        [InlineKeyboardButton("3. Nahi, itni khas zarurat toh nahi hai.", callback_data='opt3')]
    ]
    await query.edit_message_text(vision_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    return FEEDBACK

async def final_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🙏 *Thank you!* Aapka kimati waqt dene ke liye. *Passion* hamesha aapke sath hai! ✨")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(filters.Regex('^(Hii|hii|Hi|hi)$'), start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            EDUCATION: [CallbackQueryHandler(handle_edu)],
            STREAM: [CallbackQueryHandler(handle_stream)],
            HELP_REQUEST: [CallbackQueryHandler(show_vision)],
            FEEDBACK: [CallbackQueryHandler(final_step)],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    app.add_handler(conv)
    app.run_polling()

if __name__ == '__main__':
    main()