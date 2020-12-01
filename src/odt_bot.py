
import os
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

label = ''
PHOTO_NAME = 1
photo_file = None
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text("This is ODT bot (Object Detection Telegram bot), I simply run an AI model on the backend each time you send me an image. \n Please send an image and let's see what I find there")


def start(update, context):
    update.message.reply_text('Som-hi')


def receive_img(update, context):
    global photo_file
    photo_file = update.message.photo[-1].get_file()
    reply_keyboard = [os.listdir(os.getcwd()+'/../images')]
    update.message.reply_text('Photo received! On which class does this object belong to? \n If it is a new class you have to create the class first --> /cancel',
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


    return PHOTO_NAME

def save_img(update, context):
    global photo_file
    print(update.message.text)
    img_directory = os.getcwd() + '/../images/' + update.message.text
    img_name = str(len(os.listdir(img_directory))) + '.jpg'
    photo_file.download(os.path.join(img_directory, img_name))
    update.message.reply_text('Photo saved!')

    return ConversationHandler.END

def cancel(update, context):
    #logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def classes(update, context):
    """Reply with current classes"""
    reply_keyboard = [os.listdir(os.getcwd() + '/../images')]
    print(reply_keyboard)
    update.message.reply_text(
        "The classes are below, if you want to add a class please use the command /newclass",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def newclass(update, context):
    """Reply with current classes"""
    reply_keyboard = [os.listdir(os.getcwd()+'/../images')]
    print(reply_keyboard)
    update.message.reply_text(
        "The classes are below, if you want to add a class please use the command /newclass",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))



def train(update, context):
    update.message.reply_text('Training model... This may take a while, you can come back later for the results.')
    proc = subprocess.Popen(['python3', 'train_torch.py', '-tTrue'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.communicate()[0]
    update.message.reply_text(f'Done! Model with {out.decode("utf-8")[-21:-2]}%')

def video(update, context):
    global label
    label = ' '.join(context.args)
    if label == '':
        update.message.reply_text('Add the label of the object after /video')
    else:
        update.message.reply_text('Go ahead, send a video to save.')

def process_video(update, context):
    global label
    video_file = update.message.video.get_file()
    video_file.download(f'input/{label}')
    update.message.reply_text(f'Video of a {label} received! Processing...')
    label = ''
    proc = subprocess.Popen(['python3', 'video2frames.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.communicate()[0]
    update.message.reply_text(out.decode("utf-8"))


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(open('../token.txt').read()[:-1], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram

    dp.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(
         entry_points=[MessageHandler(Filters.photo, receive_img)],

         states={
             PHOTO_NAME: [MessageHandler(Filters.text, save_img)],
         },

         fallbacks=[CommandHandler('cancel', cancel)]
     )
    dp.add_handler(conv_handler)

    #dp.add_handler(CommandHandler("train", train))
    #dp.add_handler(CommandHandler("predict", predict))
    #dp.add_handler(CommandHandler("video", video))
    dp.add_handler(CommandHandler("classes", classes))
    dp.add_handler(CommandHandler("newclass", newclass))

    dp.add_handler(MessageHandler(Filters.text, echo))
    #dp.add_handler(MessageHandler(Filters.video, process_video))
    dp.add_handler(MessageHandler(Filters.photo, save_img))


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
