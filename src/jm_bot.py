import os
import logging
from google.cloud import dialogflow
import predict as pred
import train as tr
import utils
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


root = os.getcwd()
video_input_path = root + '/../input/video/input_video.mp4'
image_input_path = root + '/../input/image/input_image.jpg'
classes_directory = root + '/../images'

def echo(update, context):
    """Echo the user message."""
    text = update['message']['text']
    reply = detect_intent_texts(text)
    #print(update)
    #print(reply)
    update.message.reply_text(reply)


def detect_intent_texts(text, project_id = "wave31-webhelp-suazo", session_id = "telegram-integration", language_code = "es-ES"):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation."""
    
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))
    text_input = dialogflow.types.TextInput(
        text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(
        session=session, query_input=query_input)

    print('=' * 20)
    print('Query text: {}'.format(response.query_result.query_text))
    print('Detected intent: {} (confidence: {})\n'.format(response.query_result.intent.display_name, response.query_result.intent_detection_confidence))
    print('Fulfillment text: {}\n'.format(response.query_result.fulfillment_text))

    return response.query_result.fulfillment_text 
# [END dialogflow_detect_intent_text]

def prediction(update, context):
    image_file = update.message.photo[-1].get_file()
    image_file.download(image_input_path)

    prediction, confidence = pred.predict_telegram(image_input_path)
    update.message.reply_text("Això és {}".format(prediction))

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    #Dialogflow configuration
    
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(open('../token.txt').read()[:-1], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.photo, prediction))

    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
