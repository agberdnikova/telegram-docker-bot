#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os  # [ADDED] нужно для os.environ
import base64  # [ADDED] нужно, чтобы потом раскодировать картинку из base64

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from openai import OpenAI  # [ADDED]

# Initialize the OpenAI client with your API key.
# It is recommended to load the API key from an environment variable for security.
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])  # [спрятала ключик, чатджипити настоял]

# Enable logging
logging.basicConfig(
    format='timestamp=%(asctime)s logger=%(name)s level=%(levelname)s msg="%(message)s"',
    datefmt='%Y-%m-%dT%H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/bot.log"),
        logging.StreamHandler()
    ]
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

# <<< новый кусок для картинок >>>
async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сгенерировать изображение по тексту: /img описание"""  # [ADDED for image]
    prompt = " ".join(context.args).strip()  # [ADDED for image]
    if not prompt:  # [ADDED for image]
        await update.message.reply_text("Напиши так: /img твой_запрос_на_картинку")  # [ADDED for image]
        return  # [ADDED for image]
    await update.message.reply_text("🎨 Рисую… это может занять немного времени")  # [ADDED for image]


    try:  # [ADDED for image]
        # Генерация изображения через OpenAI  # [ADDED for image]
        res = client.images.generate(  # [ADDED for image]
            model="gpt-image-1",        # [ADDED for image]
            prompt=prompt,              # [ADDED for image]
            size="1024x1024"            # [ADDED for image] можно поменять на "1536x1024" для ландшафта
        )  # [ADDED for image]

        # OpenAI отдаёт base64 → превращаем в байты  # [ADDED for image]
        b64 = res.data[0].b64_json  # [ADDED for image]
        img_bytes = base64.b64decode(b64)  # [ADDED for image]

        # Отправляем фото в Telegram  # [ADDED for image]
        await update.message.reply_photo(photo=img_bytes, caption=f"🖼️ {prompt}")  # [ADDED for image]

    except Exception as e:  # [ADDED for image]
        await update.message.reply_text(f"Не получилось сгенерировать картинку: {e}")  # [ADDED for image]
# <<< конец нового куска >>>

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message (now via GPT)."""
    # [CHANGED] раньше бот просто повторял текст, теперь берём текст и отправляем в OpenAI
    user_message = update.message.text or ""

    # Create a chat completion request.
    # The 'messages' parameter defines the conversation history,
    # including system instructions and user prompts.
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Specify the model to use
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},  # System message sets the assistant's persona
            {"role": "user", "content": user_message},  # User's message/prompt
        ]
    )

    # Access text content from "message" within the first "Choice"
    ai_response = completion.choices[0].message.content  # [ADDED/RENAMED: ai_response]

    # [CHANGED] было: await update.message.reply_text(update.message.text)
    await update.message.reply_text(ai_response)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build() # (спрятала токен, чатджипити настоял)

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler(["img", "imagine", "image"], image_command))  # [ADDED for image]

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()