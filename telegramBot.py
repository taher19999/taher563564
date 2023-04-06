import asyncio

from telegram.constants import ChatAction

from chatGPT import ChatGPT
from telegram import Update, Message, constants
from telegram.error import RetryAfter, BadRequest
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters


class TelegramBot:
    def __init__(self, token: dict, ai: ChatGPT, allowed: [int]):
        self.bot_token = token
        self.ai = ai
        self.allowed = allowed

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /start
        """
        await update.message.reply_text("/start - Start the bot"
                                        "\n/gen - Create text"
                                        "\nMade by @SPUZ_FEED")

    def is_allowed(self, user: int) -> bool:
        """
        Check if user in allow list
        """
        return user in self.allowed

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /start
        """
        if not self.is_allowed(update.message.from_user.id):
            return

        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a @SPUZ_FEED")

    async def send_typing(self, update: Update, context: ContextTypes.DEFAULT_TYPE, every_seconds: int):
        """
        Sends the typing action
        """

        if not self.is_allowed(update.message.from_user.id):
            return

        while True:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            await asyncio.sleep(every_seconds)

    async def gen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Generates text
        """
        if not self.is_allowed(update.message.from_user.id):
            return

        typing_task = context.application.create_task(
            self.send_typing(update, context, every_seconds=4)
        )

        message_text = update.message.text[5:]
        if message_text == "":
            await context.bot.send_message(chat_id=update.effective_chat.id, text="/gen {prompt}")
        else:
            send = await context.bot.send_message(chat_id=update.effective_chat.id, text="Got request")

            text = self.ai.create_text(message_text)

            await context.bot.editMessageText(chat_id=update.effective_chat.id,
                                              message_id=send.message_id,
                                              text=f"Request done in {text.time_cons} sec")

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                reply_to_message_id=send.message_id,
                text=text.text
            )

        typing_task.cancel()

    def run(self):
        """
        Run the bot
        """
        application = ApplicationBuilder().token(self.bot_token).build()

        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('gen', self.gen))
        # application.add_handler(MessageHandler(filters.TEXT & filters.USER, self.prompt))

        application.run_polling()
