import os
import refund_ticket
import user_info
import buy_ticket
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackContext

user_info_handler = ConversationHandler(
    entry_points=[CommandHandler("user_info", user_info.start)],
    states={
        user_info.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_info.get_name)],
        user_info.SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_info.get_surname)],
        user_info.EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_info.get_email)],
        user_info.PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_info.get_phone)],
        user_info.CONFIRM: [MessageHandler(filters.Regex("^(Yes|No)$"), user_info.confirm)],
    },
    fallbacks=[CommandHandler("cancel", user_info.cancel)],
)

buy_ticket_handler = ConversationHandler(
    entry_points=[CommandHandler("buy_ticket", buy_ticket.buy_ticket)],
    states={
        buy_ticket.DEPARTURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_ticket.departure)],
        buy_ticket.DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_ticket.destination)],
        buy_ticket.DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_ticket.date)],
        buy_ticket.CONFIRM: [MessageHandler(filters.Regex("^(Yes|No)$"), buy_ticket.confirm)],
    },
    fallbacks=[CommandHandler("cancel", buy_ticket.cancel)],
)

refund_ticket_handler = ConversationHandler(
    entry_points=[CommandHandler("refund_ticket", refund_ticket.refund_ticket)],
    states={
        refund_ticket.TICKET_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, refund_ticket.ticket_id)],
        refund_ticket.EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, refund_ticket.email)],
        refund_ticket.CONFIRM: [MessageHandler(filters.Regex("^(Yes|No)$"), refund_ticket.confirm)],
    },
    fallbacks=[CommandHandler("cancel", refund_ticket.cancel)],
)

# Main function
def main() -> None:
  application = Application.builder().token(BOT_TOKEN).build()
  application.add_handler(user_info_handler)
  application.add_handler(buy_ticket_handler)
  application.add_handler(refund_ticket_handler)

  # Start the bot
  application.run_polling()

if(__name__ == "__main__"):
  main()