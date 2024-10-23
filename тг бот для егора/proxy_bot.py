import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет! Я бот для управления ключевыми словами. Используйте команды:\n'
        '/add_keyword [слово] - добавить ключевое слово\n'
        '/remove_keyword [слово] - удалить ключевое слово\n'
        '/list_keywords - показать список ключевых слов'
    )


async def forward_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from proxy_config import ADMIN_BOT_USERNAME

    message = update.message
    if message.text.startswith('/'):
        await context.bot.send_message(
            chat_id=ADMIN_BOT_USERNAME,
            text=f"User @{message.from_user.username} ({message.from_user.id}) sent command:\n{message.text}"
        )
        await message.reply_text("Команда отправлена.")


async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from proxy_config import ADMIN_BOT_USERNAME

    message = update.message
    forwarded_text = f"Message from @{message.from_user.username} ({message.from_user.id}):\n{message.text}"
    await context.bot.send_message(
        chat_id=ADMIN_BOT_USERNAME,
        text=forwarded_text
    )
    await message.reply_text("Сообщение отправлено.")


def main():
    from proxy_config import BOT_TOKEN

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.COMMAND, forward_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    application.run_polling()


if __name__ == '__main__':
    main()