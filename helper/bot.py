import logging
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

class bot:
    def __init__(self, token):
        if token == '':
            logging.error('token is empty')
            self.application = None
        else:
            self.application = ApplicationBuilder().token(token).build()

    async def start(self):
        if self.application == None:
            return

        logging.info('bot start running...')
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

    async def stop(self):
        if self.application == None:
            return

        logging.info('bot stop running...')
        await self.application.updater.stop()
        await self.application.stop()

    async def send(self, who, context=None, image=None):
        if self.application == None:
            return

        try:
            if image != None:
                await self.application.bot.send_photo(
                    chat_id=who,
                    photo=image,
                    caption=context,
                    parse_mode='MarkdownV2'
                )
            else:
                await self.application.bot.send_message(
                    chat_id=who,
                    text=context,
                    disable_web_page_preview=True,
                    parse_mode='MarkdownV2'
                )
        except Exception as e:
            logging.error(f'sending message failed: {e}')

