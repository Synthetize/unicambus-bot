import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import request

TICKET_ID, EMAIL, CONFIRM = range(3)

async def refund_ticket(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Please tell me the ticket ID.")
    return TICKET_ID

async def ticket_id(update: Update, context: CallbackContext) -> int:
    context.user_data["ticket_id"] = update.message.text
    await update.message.reply_text("What's your email?")
    return EMAIL

async def email(update: Update, context: CallbackContext) -> int:
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Please confirm your information.")
    reply_keyboard = [["Yes", "No"]]
    await update.message.reply_text(
        f"You want to refund ticket with ID {context.user_data['ticket_id']} and email {context.user_data['email']}?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CONFIRM

async def confirm(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == "yes":
        await update.message.reply_text("Wait a bit until I process your request.", reply_markup=ReplyKeyboardRemove())
        ticket = context.user_data["ticket_id"]
        mail = context.user_data["email"]
        res = await request.refund_ticket(ticket, mail)
        if res:
            await update.message.reply_text("Ticket refunded successfully. Check your email to complete the refund.")
        else:
            await update.message.reply_text("Failed to refund ticket.")


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Operation cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END