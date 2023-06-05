import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot states
NAME, EMAIL, PHONE_NUMBER, ADDITIONAL_PHOTOS = range(4)

count = 1


# Start command handler
def start(update: Update, context) -> int:
    global count
    count = 1
    reply_keyboard = [['/cancel']]
    update.message.reply_text(
        "እንኳን ወደ በጊዜ ሳሎን መመዝገቢያ ቦት መጡ! \n እባኮን የድርጅቶን ስም ያስገቡ",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return NAME


# Name handler
def name_handler(update: Update, context) -> int:
    user_name = update.message.text
    context.user_data['name'] = user_name
    update.message.reply_text("እባኮን የድርጅቶን email አድራሻ ያስገቡ")
    return EMAIL


# Email handler
def email_handler(update: Update, context) -> int:
    user_email = update.message.text
    context.user_data['email'] = user_email
    update.message.reply_text("እባኮን የድርጅቶን ስልክ ቁጥር ያስገቡ")
    return PHONE_NUMBER


# Phone number handler
def phone_number_handler(update: Update, context) -> int:
    user_phone_number = update.message.text
    context.user_data['phone_number'] = user_phone_number
    update.message.reply_text("እባኮን ለድርጅቶን ፕሮፋይል የሚሆኑ ፎቶ ይላኩ። \n ሲጨርሱ Done ብለዉ ይላኩ ")

    return ADDITIONAL_PHOTOS


# Additional photos handler

def additional_photos_handler(update: Update, context) -> int:
    global count
    if 'additional_photos' not in context.user_data:
        context.user_data['additional_photos'] = []

    if update.message.photo:
        user_additional_photo = update.message.photo[-1].get_file()
         user_additional_photo.download('{}_additional_photo_{}.jpg'.format(update.message.from_user.id,
                                                                           len(context.user_data[
                                                                                   'additional_photos']) + 1))
        context.user_data['additional_photos'].append(
            '{}_additional_photo_{}.jpg'.format(update.message.from_user.id,
                                                len(context.user_data['additional_photos']) + 1))

    elif update.message.text.lower() == 'done':
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="\nName: {}\nEmail: {}\nPhone Number: {}".format(context.user_data['name'],
                                                                                       context.user_data['email'],
                                                                                       context.user_data[
                                                                                           'phone_number']))
        for additional_photo in context.user_data['additional_photos']:
            update.message.reply_text(f'የድርጅቶ ፕሮፋይል ፎቶ {count}:')
            count += 1
            context.bot.send_photo(chat_id=update.message.chat_id, photo=open(additional_photo, 'rb'))
        update.message.reply_text("ምዝገባዎ ተጠናቆዋል። \n  ከእኛጋር ስለሰሩ እናመሰግናለን። ")

        # Forward user input information to another Telegram account
        forward_chat_id = "774009453"
        context.bot.send_message(
            chat_id=forward_chat_id,
            text="\nName: {}\nEmail: {}\nPhone Number: {}".format(
                context.user_data['name'], context.user_data['email'], context.user_data['phone_number']
            )
        )
        for additional_photo in context.user_data['additional_photos']:
            context.bot.send_photo(
                chat_id=forward_chat_id,
                photo=open(additional_photo, 'rb')
            )
        return ConversationHandler.END

    elif update.message.text.lower() != "y":
        update.message.reply_text("ምዝገባዎ ተቆዋርጦዋል እንደገና ለማስጀመር /start ብለዉ ይላኩ ")

    return ADDITIONAL_PHOTOS


def cancel(update: Update, context) -> int:
    context.user_data.clear()
    update.message.reply_text('ምዝገባዎ ተቆዋርጦዋል እንደገና ለማስጀመር /start ብለዉ ይላኩ.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# Create the EventHandler and pass it your bot's token
updater = Updater("5662826292:AAEsqDQoYj8xxkIJ8UDwAyaAD7dEe2zK--c", use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher

# Create conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        NAME: [MessageHandler(Filters.text & ~Filters.command, name_handler)],
        EMAIL: [MessageHandler(Filters.text & ~Filters.command, email_handler)],
        PHONE_NUMBER: [MessageHandler(Filters.text & ~Filters.command, phone_number_handler)],
        ADDITIONAL_PHOTOS: [MessageHandler(Filters.photo | Filters.text & ~Filters.command, additional_photos_handler)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    allow_reentry=True
)

# Add conversation handler to the dispatcher
dp.add_handler(conv_handler)
print("Program started...")

# Start the bot
updater.start_polling()

# Run the bot until Ctrl+C is pressed
updater.idle()
