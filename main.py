import logging
import mysql.connector
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot states
NAME, PHOTO, EMAIL, PHONE_NUMBER, ADDITIONAL_PHOTOS = range(5)

# MySQL database configuration
db_config = {
    'user': 'Mihiretu',
    'password': 'Tsi@mt14',
    'host': 'Mihiretu.mysql.pythonanywhere-services.com',
    'database': 'Mihiretu$default'
}

count = 1
# Start command handler
def start(update: Update, context) -> int:
    reply_keyboard = [['Cancel']]
    update.message.reply_text(
        "Welcome to Begize Salon!\n Please enter your organization name",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return NAME


# Name handler
def name_handler(update: Update, context) -> int:
    user_name = update.message.text
    context.user_data['name'] = user_name
    update.message.reply_text("Your organization name: {}".format(user_name))
    update.message.reply_text("Please insert your license scanned photo.")
    return PHOTO


# Photo handler
def photo_handler(update: Update, context) -> int:
    user_photo = update.message.photo[-1].get_file()
    user_photo.download('{}_photo.jpg'.format(update.message.from_user.id))
    update.message.reply_text("Your license:")
    context.bot.send_photo(chat_id=update.message.chat_id,
                           photo=open('{}_photo.jpg'.format(update.message.from_user.id), 'rb'))
    update.message.reply_text("Please enter your email address.")

    return EMAIL


# Email handler
def email_handler(update: Update, context) -> int:
    user_email = update.message.text
    context.user_data['email'] = user_email
    update.message.reply_text("Your email: {}".format(user_email))
    update.message.reply_text("Please enter your phone number.")

    return PHONE_NUMBER


# Phone number handler
def phone_number_handler(update: Update, context) -> int:
    user_phone_number = update.message.text
    context.user_data['phone_number'] = user_phone_number
    update.message.reply_text("Your phone number: {}".format(user_phone_number))
    update.message.reply_text("Please send photos for your organization profile. Send 'Done' when you finish.")
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
        update.message.reply_text(f'Profile photo {count}:')
        count+=1
        context.bot.send_photo(chat_id=update.message.chat_id,
                               photo=open('{}_additional_photo_{}.jpg'.format(update.message.from_user.id,
                                                                              len(context.user_data[
                                                                                      'additional_photos'])), 'rb'))
    elif update.message.text.lower() == 'done':
        update.message.reply_text("Your registration is completed. Thanks for your information!")

        # Forward user input information to another Telegram account
        forward_chat_id = "774009453"
        context.bot.send_message(
            chat_id=forward_chat_id,
            text="\nName: {}\nEmail: {}\nPhone Number: {}".format(
                context.user_data['name'], context.user_data['email'], context.user_data['phone_number']
            )
        )
        context.bot.send_photo(
            chat_id=forward_chat_id,
            photo=open('{}_photo.jpg'.format(update.message.from_user.id), 'rb')
        )

        for additional_photo in context.user_data['additional_photos']:
            context.bot.send_photo(
                chat_id=forward_chat_id,
                photo=open(additional_photo, 'rb')
            )

        # Store user input information in MySQL database
        cnx = mysql.connector.connect(**db_config)
        if cnx.is_connected():
            print("Connected to the database.")
        cursor = cnx.cursor()
        #Mihiretu$default

        # Insert user information into the 'users' table
        insert_query = "INSERT INTO users (name, email, phone_number) VALUES (%s, %s, %s)"
        user_info = (context.user_data['name'], context.user_data['email'], context.user_data['phone_number'])
        cursor.execute(insert_query, user_info)
        user_id = cursor.lastrowid

        # Insert user photos into the 'photos' table
        insert_photo_query = "INSERT INTO photos (user_id, photo_url) VALUES (%s, %s)"
        photo_urls = ['{}_photo.jpg'.format(update.message.from_user.id)]
        photo_urls += context.user_data['additional_photos']
        photo_data = [(user_id, url) for url in photo_urls]
        cursor.executemany(insert_photo_query, photo_data)

        cnx.commit()
        cursor.close()
        cnx.close()

        return ConversationHandler.END

    return ADDITIONAL_PHOTOS


def cancel(update: Update, context) -> int:
    context.user_data.clear()
    update.message.reply_text('Operation cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# Create the EventHandler and pass it your bot's token
updater = Updater("6212045014:AAHuMd2jHr_Ly9zKZxnVdPjH1cKd-749H-w", use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher

# Create conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        NAME: [MessageHandler(Filters.text & ~Filters.command, name_handler)],
        PHOTO: [MessageHandler(Filters.photo, photo_handler)],
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
