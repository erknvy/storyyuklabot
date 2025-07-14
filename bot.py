from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from instagrapi import Client

REQUIRED_CHANNEL = "@welic_pg"
BOT_TOKEN = "8062422910:AAEwqK_P8z3P-yKVapKh48lt48Gq6_cEU3U"

cl = Client()
cl.login("testapp0825", "Maktabimiz_0825")

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_photo(
            photo="https://i.imgur.com/ht5Uydz.png",
            caption=(
                "👋 Bu bot Instagram <b>istorialarini</b> yuklaydi."
                f"📢 Botdan foydalanish uchun <b>{REQUIRED_CHANNEL}</b> kanaliga obuna bo‘ling."
                "✅ So‘ngra username’ni <b>@belgisi bilan</b> yuboring. Masalan: <code>@erkinovy__5</code>"
            ),
            parse_mode="HTML"
        )

# Obuna tekshiruv
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print("[XATO] Obuna tekshiruvda:", e)
        return False

# Username kelganda story yuklash
async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    is_subscribed = await check_subscription(user_id, context)

    if not is_subscribed:
        await update.message.reply_text(
            f"📢 Iltimos, {REQUIRED_CHANNEL} kanaliga obuna bo‘ling. So‘ng qayta urinib ko‘ring.",
            disable_web_page_preview=True
        )
        return

    text = update.message.text.strip()

    if not text.startswith("@"):
        await update.message.reply_text(
            "❗ Username’ni <b>@belgisi bilan</b> kiriting. Masalan: <code>@instagram</code>",
            parse_mode="HTML"
        )
        return

    username = text[1:]
    if not username.replace(".", "").replace("_", "").isalnum():
        await update.message.reply_text(
            "📛 Username noto‘g‘ri. Faqat harf, raqam, nuqta va _ bo‘lishi mumkin.",
            parse_mode="HTML"
        )
        return

    loading_msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        user = cl.user_info_by_username_v1(username)
        user_id = user.pk
        stories = cl.user_stories(user_id)

        if not stories:
            await loading_msg.delete()
            await update.message.reply_text("📭 Bu foydalanuvchida aktiv story yo‘q.")
            return

        success = False

        for story in stories:
            url = story.video_url or story.thumbnail_url
            if url:
                if story.video_url:
                    await update.message.reply_video(video=str(url))
                else:
                    await update.message.reply_photo(photo=str(url))
                success = True

        await loading_msg.delete()

        if not success:
            await update.message.reply_text("📭 Story mavjud, lekin yuklab bo‘lmadi.")

    except Exception as e:
        print("[XATO]", e)
        await loading_msg.delete()
        await update.message.reply_text("❌ Xatolik: Foydalanuvchi topilmadi yoki ma’lumotlar olinmadi.")

# Boshqa xabarlar
async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "📌 Faqat Instagram username’ni <b>@belgi bilan</b> yozing. Masalan: <code>@cristiano</code>",
            parse_mode="HTML"
        )

# Botni ishga tushirish
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    app.add_handler(MessageHandler(~filters.TEXT, unknown_message))

    print("✅ Bot ishga tushdi...")
    app.run_polling()
