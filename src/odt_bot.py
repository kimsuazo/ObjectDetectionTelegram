import os
import logging
import predict as pred
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

label = ''
SAVE_IMG, SAVE_IMG_CLASS = 1, 2
photo_file = None
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def echo(update, context):
    """Echo the user message."""
    reply_keyboard = [["/Train", "/Predict", ["/Upload"]]]
    update.message.reply_text("This is ODT bot (Object Detection Telegram bot), I simply run an AI model on the backend each time you send me an image. \n Please send an image and let's see what I find there",
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

def start(update, context):
    update.message.reply_text('Som-hi')


def choose_update(update, context):
    update.message.reply_text("Which kind of file do you want to upload?",
                            reply_markup=ReplyKeyboardMarkup[["Video", "Photo"]], one_time_keyboard=True)

    return set_update

def receive_img(update, context):
    global photo_file
    reply_keyboard = []
    photo_file = update.message.photo[-1].get_file()
    reply_keyboard = [os.listdir(os.getcwd()+'/../images')]
    reply_keyboard.append(["new class"])
    update.message.reply_text('Photo received! On which class does this object belong to? \n If it is a new class you have to create the class first --> /cancel',
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SAVE_IMG

def save_img(update, context):
    global photo_file

    if update.message.text == "new class":
        update.message.reply_text('Please give a name for the new class:')
        return SAVE_IMG_CLASS

    img_directory = os.getcwd() + '/../images/' + update.message.text
    img_name = update.message.text +"_" + str(len(os.listdir(img_directory))) + '.jpg'
    photo_file.download(os.path.join(img_directory, img_name))
    update.message.reply_text('Photo saved!')

    return ConversationHandler.END

def save_img_class(update, context):
    global photo_file
    
    img_directory = os.getcwd() + '/../images/' + update.message.text
    os.mkdir(img_directory)
    img_name = update.message.text +"_" + str(len(os.listdir(img_directory))) + '.jpg'
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


def predict(update, context):
    global photo_file

    photo_file = update.message.photo[-1].get_file()
    img_path = os.getcwd() + "/../predict/image.jpg"
    photo_file.download(img_path)


    prediction, confidence = pred.predict_telegram(img_path)
    
    update.message.reply_text('The class is {} with a confidence of {}'.format(prediction, confidence))


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

    ####    START COMMAND    ####
    dp.add_handler(CommandHandler("start", start))

    ####    UPLOAD PIPELINE    ####
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("Upload", choose_update)],
        states={
            SET_UPDATE: []
            RECEIVE_IMG: [MessageHandler(Filters.photo, receive_img)],
            SAVE_IMG: [MessageHandler(Filters.text, save_img)],
            SAVE_IMG_CLASS: [MessageHandler(Filters.text, save_img_class)],
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
    dp.add_handler(MessageHandler(Filters.photo, predict))


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
