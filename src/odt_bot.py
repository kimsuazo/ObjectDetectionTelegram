import os
import logging
import predict as pred
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

RECEIVE_VIDEO, SAVE_VIDEO, SAVE_VIDEO_CLASS, RECEIVE_IMAGE, SAVE_IMAGE, SAVE_IMAGE_CLASS = range(6)

root = os.getcwd()
video_input_path = root + '/../input/video/input_video.mp4'
image_input_path = root + '/../input/image/input_image.jpg'
classes_directory = root + '/../images'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def echo(update, context):
    """Echo the user message."""
    reply_keyboard = [["/Train", "/Predict"], ["/Upload", "/Classes"]]
    update.message.reply_text("This is ODT bot (Object Detection Telegram bot), I am a Machine Learning interface that currently runs only an Object Classification model. \n What do you want to do?",
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

def start(update, context):
    reply_keyboard = [["/Train", "/Predict"], ["/Upload", "/Classes"]]
    update.message.reply_text("This is ODT bot (Object Detection Telegram bot), I am a Machine Learning interface that currently runs only an Object Classification model. \n What do you want to do?",
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))


####    UPLOAD PIPELINE    ####

def choose_upload(update, context):
    update.message.reply_text("Which kind of file do you want to upload?",
                            reply_markup=ReplyKeyboardMarkup([["/Video"], ["/Image"]]), one_time_keyboard=True)

####    VIDEO PIPELINE    ####

def set_video(update, context):
    update.message.reply_text("Please send me a video! \nTake into account to move the phone around the object so I can learn better this object.")
    
    return RECEIVE_VIDEO

def receive_video(update, context):
    video_file = update.message.video[-1].get_file()
    video_file.download(video_input_path)

    reply_keyboard = []
    reply_keyboard = [os.listdir(classes_directory)]
    reply_keyboard.append(["new class"])
    update.message.reply_text('Photo received! On which class does this object belong to? ',
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SAVE_VIDEO

def save_video(update, context):

    if update.message.text == "new class":
        update.message.reply_text('Please give a name for the new class:')
        return SAVE_VIDEO_CLASS

    class_directory = os.path.join(classes_directory, update.message.text)
    utils.video2frames(video_input_path, class_directory)
    update.message.reply_text('Photo saved!')

    return ConversationHandler.END

def save_video_class(update, context):
    
    class_directory = os.path.join(classes_directory, update.message.text)
    os.mkdir(img_directory)
    utils.video2frames(video_input_path, class_directory)
    update.message.reply_text('Photo saved!')

    return ConversationHandler.END


####    IMAGE PIPELINE    ####

def set_image(update, context):
    update.message.reply_text("Please send me an image!")
    
    return RECEIVE_IMAGE

def receive_image(update, context):
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(image_input_path)

    reply_keyboard = []
    reply_keyboard = [os.listdir(classes_directory)]
    reply_keyboard.append(["new class"])
    update.message.reply_text('Photo received! On which class does this object belong to?',
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SAVE_IMAGE

def save_image(update, context):
    if update.message.text == "new class":
        update.message.reply_text('Please give a name for the new class:')
        return SAVE_IMAGE_CLASS

    class_directory = os.path.join(classes_directory, update.message.text)
    image_name = update.message.text + "_" + str(len(os.listdir(class_directory))) + '.jpg'
    image_name = os.path.join(class_directory, image_name)
    os.rename(image_input_path, image_name)
    update.message.reply_text('Photo saved!')

    return ConversationHandler.END

def save_image_class(update, context):
    
    class_directory = os.path.join(classes_directory, update.message.text)
    os.mkdir(class_directory)
    image_name = update.message.text + "_" + str(len(os.listdir(class_directory))) + '.jpg'
    image_name = os.path.join(class_directory, image_name)
    os.rename(image_input_path, image_name)
    update.message.reply_text('Photo saved!')

    return ConversationHandler.END

def cancel(update, context):
    #logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

#####################################################################################################

def classes(update, context):
    """Reply with current classes"""
    reply_keyboard = [os.listdir(classes_directory)]
    print(reply_keyboard)
    update.message.reply_text(
        "The classes are below:",
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
    photo_file = update.message.photo[-1].get_file()
    img_path = os.getcwd() + "/../input/predict/image.jpg"
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
    dp.add_handler(CommandHandler("Upload", choose_upload))

    ####    UPLOAD PIPELINE    ####
    video_pipeline = ConversationHandler(
        entry_points=[CommandHandler("Video", set_video)],
        states={
            #Video pipeline
            RECEIVE_VIDEO: [MessageHandler(Filters.video, receive_video)],
            SAVE_VIDEO: [MessageHandler(Filters.text, save_video)],
            SAVE_VIDEO_CLASS: [MessageHandler(Filters.text, save_video_class)], 
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    image_pipeline = ConversationHandler(
        entry_points=[CommandHandler("Image", set_image)],
        states={
            #Image pipeline
            RECEIVE_IMAGE: [MessageHandler(Filters.photo, receive_image)],
            SAVE_IMAGE: [MessageHandler(Filters.text, save_image)],
            SAVE_IMAGE_CLASS: [MessageHandler(Filters.text, save_image_class)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(video_pipeline)
    dp.add_handler(image_pipeline)


    #dp.add_handler(CommandHandler("train", train))
    dp.add_handler(CommandHandler("predict", predict))
    #dp.add_handler(CommandHandler("video", video))
    dp.add_handler(CommandHandler("classes", classes))

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
