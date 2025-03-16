import json

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import request

DEPARTURE, DESTINATION, DATE, CONFIRM = range(4)


async def buy_ticket(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Please tell me your starting location.")
    return DEPARTURE


async def departure(update: Update, context: CallbackContext) -> int:
    context.user_data["departure_location"] = update.message.text
    await update.message.reply_text("What's your destination?")
    return DESTINATION


async def destination(update: Update, context: CallbackContext) -> int:
    context.user_data["destination_location"] = update.message.text
    await update.message.reply_text("What's the date of your travel?")
    return DATE


async def date(update: Update, context: CallbackContext) -> int:
    context.user_data["date"] = update.message.text
    await update.message.reply_text("Please confirm your information.")
    reply_keyboard = [["Yes", "No"]]
    await update.message.reply_text(
        "You want to travel: \n"
        f"from {context.user_data["departure_location"]}\n"
        f"to {context.user_data["destination_location"]}\n"
        f"on {context.user_data["date"]}\n",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CONFIRM


async def confirm(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == "yes":
        await update.message.reply_text("Great! I will proceed with the booking.", reply_markup=ReplyKeyboardRemove())
        departure_id = find_location_id(context.user_data["departure_location"])
        destination_id = find_location_id(context.user_data["destination_location"])
        formatted_date = "-".join(reversed(context.user_data["date"].split("-")))
        user_info = get_user_info_by_id(update.message.chat_id)
        await update.message.reply_text(
            f"Departure ID: {departure_id}\n"
            f"Destination ID: {destination_id}\n"
            f"Date: {formatted_date}\n"
            f"UserID: {update.message.chat_id}\n"
            f"Name: {user_info.get('name')}\n"
            f"Surname: {user_info.get('surname')}\n"
            f"Email: {user_info.get('email')}\n"
            f"Phone: {user_info.get('phone')}\n"
        )

        request.book_ticket(departure_id, destination_id, formatted_date, user_info.get('email'), user_info.get('name'),
                            user_info.get('surname'), user_info.get('phone'))
        return ConversationHandler.END
    else:
        await update.message.reply_text("Ok, let's start over. Please tell me your departing location",
                                        reply_markup=ReplyKeyboardRemove())
        return DEPARTURE


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("The conversation has been cancelled.")
    return ConversationHandler.END


def find_location_id(departure_location: str) -> int:
    with open("data/stops.json") as file:
        stops = json.load(file)
        for stop in stops:
            if stop["name"] == departure_location:
                return stop["id"]
    raise Exception(f'Invalid stop name {departure_location}')

def get_user_info_by_id(user_id: int) -> dict:
    with open("data/users.json") as file:
        users = json.load(file)
        return users.get(str(user_id), {})