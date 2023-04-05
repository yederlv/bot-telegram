#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Accede a una variable de entorno específica
TOKEN = os.getenv('TOKEN')

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ForceReply
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

## ------------------------------
import json
from math import radians, sin, cos, sqrt, atan2

def distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = sin(dLat/2) * sin(dLat/2) + cos(radians(lat1)) \
        * cos(radians(lat2)) * sin(dLon/2) * sin(dLon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c  # Distance in km

def find_nearest_agency(user_lat, user_lon):
    with open('data.json') as f:
        agencies = json.load(f)

    nearest_agency = None
    min_distance = float('inf')

    for agency in agencies:
        lat, lon = agency['latitude'], agency['longitude']
        d = distance(user_lat, user_lon, lat, lon)
        if d < min_distance:
            min_distance = d
            nearest_agency = agency

    return nearest_agency

## ------------------------------

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)
    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["Si", "No"]]
    # user = update.effective_user 
    user = update.message.from_user

    await update.message.reply_text(
        f"Hola {user.first_name}! te ayudamos a brindarte el cine más cercano a tu ubicación.\n"        
        "Aceptas el tratamiento de tus datos? 😁\n\n"
        "Envia /cancelar si no quieres seguir con la conversación. 🙄",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Si o No?"
        ),
    )

    return GENDER  # imprime si o no en consola


async def gender(update: Update, Context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Genial! envía tu ubicación actual! 🗺"
    )
    return GENDER


# async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Stores the selected gender and asks for a photo."""
#     user = update.message.from_user
#     logger.info("Gender of %s: %s", user.first_name, update.message.text)
#     await update.message.reply_text(
#         "I see! Please send me a photo of yourself, "
#         "so I know what you look like, or send /skip if you don't want to.",
#         reply_markup=ReplyKeyboardRemove(),
#     )

#     return PHOTO


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "Genial! envía tu ubicación actual! 🗺\n "
        "o envia /skip si no quieres.  🙄",
        reply_markup=ReplyKeyboardRemove(),
    )

    return LOCATION


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
    )

    return LOCATION


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    await update.message.reply_text(
        "I bet you look great! Now, send me your location please, or send /skip."
    )

    return LOCATION


# async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Stores the location and asks for some info about the user."""
#     user = update.message.from_user
#     user_location = update.message.location
#     logger.info(
#         "Location of %s: Latitude: %f / Longitude: %f", user.first_name, user_location.latitude, user_location.longitude
#     )
#     await update.message.reply_text(
#         "Quizá pueda visitarte alguna vez. Por último, cuéntame algo sobre ti."
#     )

#     return BIO

#################################

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    
    logger.info(
        "Location of %s: Latitude: %f / Longitude: %f", user.first_name, user_location.latitude, user_location.longitude
    )

    nearest_agency = find_nearest_agency(user_location.latitude, user_location.longitude)
    # if nearest_agency:
    #     message = f"The nearest agency is {nearest_agency['name']}, located at ({nearest_agency['latitude']}, {nearest_agency['longitude']})."
    # else:
    #     message = "No agencies found."
    # await update.message.reply_text(message)
    await update.message.reply_text(f"El Cine más cercana es: {nearest_agency['agency']}\n Dirección 🗺: {nearest_agency['address']}")
    logger.info(
        rf"Cliente {user.first_name} | Cine : {nearest_agency['agency']}"
    )

    return BIO


############################3333333



async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "🥴 Gracias!, entonces cuéntame algo de ti"
    )

    return BIO


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Gracias. Espero que podamos volver a hablar algún día.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye Bye! 👨‍💻 Tu cuenta de credito fue hackeado...!",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            # GENDER: [MessageHandler(filters.Regex("^(Si|No)$"), gender)],
            GENDER: [MessageHandler(filters.Regex("^(Si|No)$"), gender)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            LOCATION: [
                MessageHandler(filters.LOCATION, location),
                CommandHandler("skip", skip_location),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancelar", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()