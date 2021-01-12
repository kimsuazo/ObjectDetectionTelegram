import os
import logging
import predict as pred
import train as tr
import utils
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
    update.message.reply_text("What do you want to do?",
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

def start(update, context):
    reply_keyboard = [["/Train", "/Predict"], ["/Upload", "/Classes"]]
    update.message.reply_text("This is ODT bot (Object Detection Telegram bot), I am a Machine Learning interface that currently runs only an Object Classification model. \n What do you want to do?",
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))


####    UPLOAD PIPELINE    ####

def choose_upload(update, context):
    update.message.reply_text("Which kind of file do you want to upload?\n/Cancel",
                            reply_markup=ReplyKeyboardMarkup([["/Video"], ["/Image"]]), one_time_keyboard=True)

####    VIDEO PIPELINE    ####

def set_video(update, context):
    update.message.reply_text("Please send me a 10 seconds video! \nTake into account to move the phone around the object so I can learn better this object.\n/Cancel")
    
    return RECEIVE_VIDEO

def receive_video(update, context):
    video_file = update.message.video.get_file()
    video_file.download(video_input_path)

    reply_keyboard = []
    reply_keyboard = [os.listdir(classes_directory)]
    reply_keyboard.append(["new class"])
    update.message.reply_text('Video received! On which class does this object belong to? \n/Cancel',
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SAVE_VIDEO

def save_video(update, context):

    if update.message.text == "new class":
        update.message.reply_text('Please give a name for the new class: \n/Cancel')
        return SAVE_VIDEO_CLASS

    class_directory = os.path.join(classes_directory, update.message.text)
    utils.video2frames(video_input_path, class_directory, update.message.text)
    update.message.reply_text('Video saved!   ---> return to /Menu')

    return ConversationHandler.END

def save_video_class(update, context):
    
    class_directory = os.path.join(classes_directory, update.message.text)
    os.mkdir(class_directory)
    utils.video2frames(video_input_path, class_directory, update.message.text)
    update.message.reply_text('Video saved!   ---> return to /Menu')

    return ConversationHandler.END


####    IMAGE PIPELINE    ####

def set_image(update, context):
    update.message.reply_text("Please send me an image!\n/Cancel")
    
    return RECEIVE_IMAGE

def receive_image(update, context):
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(image_input_path)

    reply_keyboard = []
    reply_keyboard = [os.listdir(classes_directory)]
    reply_keyboard.append(["new class"])
    update.message.reply_text('Photo received! On which class does this object belong to? \n/Cancel',
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SAVE_IMAGE

def save_image(update, context):
    if update.message.text == "new class":
        update.message.reply_text('Please give a name for the new class: \n/Cancel')
        return SAVE_IMAGE_CLASS

    class_directory = os.path.join(classes_directory, update.message.text)
    image_name = update.message.text + "_" + str(len(os.listdir(class_directory))) + '.jpg'
    image_name = os.path.join(class_directory, image_name)
    os.rename(image_input_path, image_name)
    update.message.reply_text('Photo saved!   ---> return to /Menu')

    return ConversationHandler.END

def save_image_class(update, context):
    
    class_directory = os.path.join(classes_directory, update.message.text)
    os.mkdir(class_directory)
    image_name = update.message.text + "_" + str(len(os.listdir(class_directory))) + '.jpg'
    image_name = os.path.join(class_directory, image_name)
    os.rename(image_input_path, image_name)
    update.message.reply_text('Photo saved!   ---> return to /Menu')

    return ConversationHandler.END

def cancel(update, context):
    reply_keyboard = [["/Train", "/Predict"], ["/Upload", "/Classes"]]
    update.message.reply_text("What do you want to do?",
                                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    return ConversationHandler.END

#####################################################################################################

def classes(update, context):
    """Reply with current classes"""
    classes = os.listdir(classes_directory)
    class_string = ""
    for i in classes:
        class_string += i + "\n"

    update.message.reply_text(
        "The classes are below:\n{}".format(class_string))


def train(update, context):
    update.message.reply_text('Training model... This may take a while, you can come back later for the results.')
    accuracy = tr.train_telegram()
    update.message.reply_text("Done! Model with {} of accuracy".format(accuracy))



def predict(update, context):
    update.message.reply_text("Please send me a photo and I will tell you what I see!")

def prediction(update, context):
    image_file = update.message.photo[-1].get_file()
    image_file.download(image_input_path)

    prediction, confidence = pred.predict_telegram(image_input_path)
    update.message.reply_text("The class is {} with a confidence of {}".format(prediction, confidence))

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

    ####    COMMANDS    ####
    dp.add_handler(CommandHandler("Upload", choose_upload))
    dp.add_handler(CommandHandler("train", train))
    dp.add_handler(CommandHandler("predict", predict))
    dp.add_handler(CommandHandler("classes", classes))
    dp.add_handler(CommandHandler("menu", cancel))

    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.photo, prediction))

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
