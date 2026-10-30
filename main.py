from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
)
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

ADMINS = ["123456789"]
BANNED_USERS = set()

def is_admin(user_id):
    return str(user_id) in ADMINS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    
    if user.id in BANNED_USERS:
        await update.message.reply_text("⛔ Вы заблокированы и не можете отправлять заявки.")
        return
    
    welcome_text = """
Привет! Я бот для заявок.

Клан CCG с радостью поможет вам с вашей проблемой. Для этого нужно правильно оформить заявку.

Как написать заявку:
1. Укажите свой юзернейм (чтобы мы могли с вами связаться) и юзернейм обидчика.
2. Подробно и честно опишите ситуацию (со всеми деталями).
3. Расскажите, что вам сделали или что вам угрожают сделать.

На этом всё. Напишите заявку и ожидайте ответа.

ВАЖНО!
Никто не гарантирует, что вам обязательно помогут, так как решение зависит от участников клана.

Не спамьте заявками! Если лидер клана увидит несколько одинаковых заявок, вам не только откажут в помощи, но и внесут в чёрный список проекта. Отправляйте заявку один раз и ждите ответа.

Клан CCG — лучший выбор для помощи мирным игрокам!
Мы стараемся сделать этот мир лучше и наказываем плохих людей.
Наш ТГК канал - https://t.me/+69uzSrBvSwc2MjUy
    """
    
    keyboard = [
        [InlineKeyboardButton("Отправить заявку", callback_data='send_request')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id in BANNED_USERS:
        await query.edit_message_text(text="⛔ Вы заблокированы и не можете отправлять заявки.")
        return
    
    if query.data == 'send_request':
        instruction_text = """
📝 Пожалуйста, напишите свою заявку в следующем формате:

1. Укажите свой юзернейм (чтобы мы могли с вами связаться) и юзернейм обидчика.
2. Подробно и честно опишите ситуацию (со всеми деталями).
3. Расскажите, что вам сделали или что вам угрожают сделать.

❗️ ВАЖНО: Не спамьте заявками! Если лидер клана увидит несколько одинаковых заявок, вам не только откажут в помощи, но и внесут в чёрный список проекта.
"""
        await query.message.reply_text(instruction_text)

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    
    if user.id in BANNED_USERS:
        await update.message.reply_text("⛔ Вы заблокированы и не можете отправлять заявки.")
        return
    
    request_text = update.message.text
    await send_to_admins(context, user, request_text)
    await update.message.reply_text("✅ Ваша заявка отправлена администраторам. Ожидайте ответа.")

async def send_to_admins(context: ContextTypes.DEFAULT_TYPE, user, request_text):
    admin_message = f"🚨 Новая заявка от @{user.username} (ID: {user.id}):\n\n{request_text}"
    for admin in ADMINS:
        try:
            await context.bot.send_message(
                chat_id=admin,
                text=admin_message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Забанить", callback_data=f'ban_{user.id}')]
                ])
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения админу {admin}: {e}")

async def ban_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if not is_admin(str(query.from_user.id)):
        await query.edit_message_text(text="❌ У вас нет прав для выполнения этого действия.")
        return
    
    user_id_to_ban = int(query.data.split('_')[1])
    BANNED_USERS.add(user_id_to_ban)
    
    original_text = query.message.text
    await query.edit_message_text(text=f"{original_text}\n\n❌ ЗАБЛОКИРОВАНО администратором @{query.from_user.username}")

    try:
        await context.bot.send_message(
            chat_id=user_id_to_ban,
            text="⛔ Вы были заблокированы за нарушение правил использования бота."
        )
    except Exception as e:
        logger.error(f"Не удалось уведомить пользователя о бане: {e}")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    if not is_admin(str(user.id)):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /ban <user_id>")
        return
    
    user_id_to_ban = int(context.args[0])
    BANNED_USERS.add(user_id_to_ban)

    await update.message.reply_text(f"✅ Пользователь с ID {user_id_to_ban} забанен.")

    try:
        await context.bot.send_message(
            chat_id=user_id_to_ban,
            text="⛔ Вы были заблокированы за нарушение правил использования бота."
        )
    except Exception as e:
        logger.error(f"Не удалось уведомить пользователя о бане: {e}")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    if not is_admin(str(user.id)):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /unban <user_id>")
        return
    
    user_id_to_unban = int(context.args[0])
    if user_id_to_unban in BANNED_USERS:
        BANNED_USERS.remove(user_id_to_unban)
        await update.message.reply_text(f"✅ Пользователь с ID {user_id_to_unban} разбанен.")
    else:
        await update.message.reply_text(f"ℹ️ Пользователь с ID {user_id_to_unban} не был забанен.")

async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    
    if not is_admin(str(user.id)):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /check <user_id>")
        return
    
    user_id_to_check = int(context.args[0])
    if user_id_to_check in BANNED_USERS:
        await update.message.reply_text(f"ℹ️ Пользователь с ID {user_id_to_check} ЗАБАНЕН.")
    else:
        await update.message.reply_text(f"ℹ️ Пользователь с ID {user_id_to_check} не забанен.")

def main() -> None:
    application = Application.builder().token("YOUR_BOT_TOKEN_HERE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(ban_button_handler, pattern=r'^ban_\d+$'))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request))

    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("check", check_user))

    application.run_polling()

if __name__ == '__main__':
    main()
