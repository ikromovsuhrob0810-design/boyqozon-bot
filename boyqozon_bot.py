import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# =============================================
#   SOZLAMALAR
# =============================================
BOT_TOKEN = "8750421912:AAFLhZQu4z5FE3LnVB4LNuFCI2MOVaciU9w"
ADMIN_ID = 1490650129

# =============================================
#   BOSQICHLAR
# =============================================
ISM, TELEFON, YOSH, KURS = range(4)

KURSLAR = [
    ["🇸🇦 Arab tili"],
    ["🇬🇧 Ingliz tili"],
    ["🇹🇷 Turk tili"],
    ["📖 Ona tili va adabiyot"],
    ["🤖 Sun'iy intellekt"],
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================
#   /start
# =============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "🏫 *Boyqozon Ta'lim Markazi*ga xush kelibsiz!\n\n"
        "Yozgi intensiv kurslarga ro'yxatdan o'tish uchun "
        "quyidagi savollarga javob bering.\n\n"
        "✏️ Avval *ism va familiyangizni* yozing:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ISM


# =============================================
#   ISM
# =============================================
async def ism_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ism"] = update.message.text.strip()
    await update.message.reply_text(
        "📞 *Telefon raqamingizni* yozing:\n"
        "_(Misol: +998901234567)_",
        parse_mode="Markdown"
    )
    return TELEFON


# =============================================
#   TELEFON
# =============================================
async def telefon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["telefon"] = update.message.text.strip()
    await update.message.reply_text(
        "🎂 *Yoshingizni* yozing:\n_(Misol: 17)_",
        parse_mode="Markdown"
    )
    return YOSH


# =============================================
#   YOSH
# =============================================
async def yosh_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    yosh = update.message.text.strip()
    if not yosh.isdigit():
        await update.message.reply_text("❗ Iltimos, yoshingizni raqamda yozing. Misol: 17")
        return YOSH
    context.user_data["yosh"] = yosh
    await update.message.reply_text(
        "📚 Qaysi *kursga* yozilmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(KURSLAR, one_time_keyboard=True, resize_keyboard=True)
    )
    return KURS


# =============================================
#   KURS
# =============================================
async def kurs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kurs = update.message.text.strip()
    valid = [k[0] for k in KURSLAR]
    if kurs not in valid:
        await update.message.reply_text(
            "❗ Iltimos, quyidagi tugmalardan birini tanlang:",
            reply_markup=ReplyKeyboardMarkup(KURSLAR, one_time_keyboard=True, resize_keyboard=True)
        )
        return KURS

    context.user_data["kurs"] = kurs
    data = context.user_data

    # Foydalanuvchiga tasdiqlash
    await update.message.reply_text(
        "✅ *Ro'yxatdan o'tdingiz!*\n\n"
        f"👤 Ism: {data['ism']}\n"
        f"📞 Telefon: {data['telefon']}\n"
        f"🎂 Yosh: {data['yosh']}\n"
        f"📚 Kurs: {data['kurs']}\n\n"
        "📲 Tez orada ustoz siz bilan bog'lanadi!\n"
        "Savollar uchun: +998 94 027 08 10",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

    # Adminga xabar
    user = update.effective_user
    tg_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    admin_msg = (
        "🔔 *Yangi ro'yxatdan o'tish!*\n\n"
        f"👤 Ism: {data['ism']}\n"
        f"📞 Telefon: {data['telefon']}\n"
        f"🎂 Yosh: {data['yosh']}\n"
        f"📚 Kurs: {data['kurs']}\n"
        f"💬 Telegram: {tg_info}"
    )
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_msg,
        parse_mode="Markdown"
    )

    return ConversationHandler.END


# =============================================
#   BEKOR QILISH
# =============================================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Ro'yxatdan o'tish bekor qilindi.\n"
        "Qayta boshlash uchun /start yozing.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# =============================================
#   MAIN
# =============================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ISM:    [MessageHandler(filters.TEXT & ~filters.COMMAND, ism_handler)],
            TELEFON:[MessageHandler(filters.TEXT & ~filters.COMMAND, telefon_handler)],
            YOSH:   [MessageHandler(filters.TEXT & ~filters.COMMAND, yosh_handler)],
            KURS:   [MessageHandler(filters.TEXT & ~filters.COMMAND, kurs_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    logger.info("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
