import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

# States for the conversation
NAME, SURNAME, EMAIL, PHONE, CONFIRM = range(5)

# Path to the JSON file
USERS_FILE = "data/users.json"


# Function to load user data from the JSON file
def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}  # Return an empty dictionary if the file doesn't exist
    except json.JSONDecodeError:
        return {}  # Return an empty dictionary in case of JSON read errors


# Function to save user data into the JSON file
def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


def does_user_exist(user_id):
    return True


# Entry point for the conversation
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "I need to collect some information to start buying bus tickets."
    )

    await update.message.reply_text(
        "If you already have information saved, you can stop by typing /cancel."
    )

    await update.message.reply_text(
        "Please tell me your name."
    )

    return NAME


# Get the user's first name
async def get_name(update: Update, context: CallbackContext) -> int:
    context.user_data["name"] = update.message.text
    await update.message.reply_text("What's your surname?")
    return SURNAME


# Get the user's surname
async def get_surname(update: Update, context: CallbackContext) -> int:
    context.user_data["surname"] = update.message.text
    await update.message.reply_text("What's your email?")
    return EMAIL


# Get the user's email
async def get_email(update: Update, context: CallbackContext) -> int:
    context.user_data["email"] = update.message.text
    await update.message.reply_text("What's your phone number?")
    return PHONE


# Get the user's phone number and ask for confirmation
async def get_phone(update: Update, context: CallbackContext) -> int:
    context.user_data["phone"] = update.message.text
    reply_keyboard = [["Yes", "No"]]
    await update.message.reply_text(
        f"Are these details correct?\n"
        f"Name: {context.user_data['name']}\n"
        f"Surname: {context.user_data['surname']}\n"
        f"Email: {context.user_data['email']}\n"
        f"Phone: {context.user_data['phone']}",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CONFIRM


# Confirm and save the data in the JSON file
async def confirm(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == "yes":
        # Get the user's chat ID
        user_id = str(update.message.chat_id)
        # Load current user data from the JSON file
        users = load_users()
        # Save user data for the current user
        users[user_id] = {
            "name": context.user_data["name"],
            "surname": context.user_data["surname"],
            "email": context.user_data["email"],
            "phone": context.user_data["phone"],
        }
        # Write the updated user data to the JSON file
        save_users(users)
        await update.message.reply_text("Your data has been saved. ✅",
                                        reply_markup=ReplyKeyboardRemove())
        print(f"Saved data: {users[user_id]}")  # Debug
    else:
        await update.message.reply_text("Okay, let's try again. Please tell me your name.")
        return NAME  # Restart the conversation

    return ConversationHandler.END


# Cancel the conversation
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Conversation canceled. ❌", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
