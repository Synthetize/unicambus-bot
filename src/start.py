import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the Bus Ticket Bot! Use the Menu button to see the available commands.")
