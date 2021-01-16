import os
import logging
import dialogflow_v2 as dialogflow
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

def start(update, context):
    update.message.reply_text("Hola, sóc el Joan Manel Comballa. Tu deus ser la detectiva Marta oi?\
Això de que el Pere hagi desaparegut em té desesperat i m'agradaria ajudar-te en tot el possible.\
Suposo que no has començat a inspeccionar el seu pis encara, el tiu sempre parlava d'una maleta i de que \
li agradaria marxar, però això d'estar tants dies sense dir res m'està començant a espantar. A veure si pots trobar la maleta, crec que estava al menjador, \
quan la trobis envia'm una foto i et diré si és la maleta que toca.\
")

def paris(update, context):
    update.message.reply_text("Oleeee! Ja has descobert què ha passat! En Pere no era més que el protagonista de “la merda se’ns menja” dels amics de les arts. \n\
No sé quant deu haver durat el joc de pistes, hem estat una setmaneta preparant-lo però ja feia temps que ens rondava pel cap. El Pere en realitat sóc una mica\
 jo (ara parla el Kimxu) tot i que hi hagi coses que no quadrin:\n\
Ho tinc tot mil·limetrat.\n\
Sempre et dic que no em queda bé la barba.\n\
No vaig en metro des de Joanic a Verdeguer però també et guardaria seient. \n\
Aquí la merda no se’ns menja pas, però també vull pagar una hipoteca amb tu.\n\
De maleïr els dilluns en sabem força i de paraigües no en tenim (la Cristo i el Pepo l’han hagut de portar…).\n\
A sobre lo de “no sóc massa guapo però sóc molt divertit” em va nikelao hehe.\n\n\
Avui és el teu cumple i vull que siguis feliç, perquè t'estimo un munt i perquè fas que cada dia sigui emocionant! \n\
Però amb lo espabilada que ets segur que has notat que falta algo de la cançó, que si, que el Pere aquest imaginari està a Paris i bla bla bla, però l’objectiu de tot això és poder\
 comprovar que París et queda bé, a tu. Així que ja et deus imaginar quin és l’últim regal de tots :). \n/VeureRegal")
 
def VeureRegal(update, context):

    foto_paris = open("../paris.jpeg", "rb")
    #print(dir(update.message))
    update.message.reply_photo(foto_paris)
    update.message.reply_text("Que es n'anem a Paris cuquii! El primer lloc que podrem posar al mapamundi de suro i el primer lloc on ens farem una foto polaroid\n\
El primer de molts llocs evidentment, perquè tinc ganes de veure món amb tu, t'estimo!")


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

    objectes = {"Maleta" : " Sii, aquesta és la maleta d'en Pere!, que estrany que no se l'hagi endut, si hi ha roba a dins, posa-te-la! \n\
Si no ha agafat la maleta, em temo que tampoc haurà agafat cap dels objectes dels que em parlava sempre, un dia em va explicar que tenia un \
objecte guardat a cada habitació, mira que n'és de vedell! \n\
Hi ha un objecte a l'estudi que deia que li serviria per executar un pla amb precisió, no se ben bé de quin objecte parlava, a veure si el pots trobar!\
", 
    			"Regla": " Claar, un regle! Com no se m’havia acudit!?\n\
En fi, en Pere és un bon mito, sempre deixa codis secrets per aquí i per allà, potser aquest regle et serveix d’alguna cosa…\n\
Pel que fa al següent objecte es troba al dormitori, busca bé que aquest el tenia ben amagat, és una mica xafarder el noi :S", 

    			"Maquina afeitar": "Una màquina d’afeitar? Aquesta sí que no me l’esperava, la veritat és que el Pere no en té gaire de barba, això sí, de màquines en té unes quantes.\n\
El següent objecte es troba al vestidor, i em sembla que tindràs feina per trobar-lo perquè hi ha un futimer de coses. A ell li agradava anar sempre preparat per\
 les adversitats, així que alguna cosa hi deu haver al vestidor que necessites, o no?", 

    			"Binocles": "Uns binòcles… Farem veure que no ho hem vist, però si que ho hem vist amb els binòcles ehh hehehe…\n\
Al que anem, amb els binòcles recordo que sempre mirava pel balcó, no sé mai que buscava, potser trobes alguna informació útil.\n\
Ah, i el següent objecte es troba al bany, sempre va arregladet el noi…", 

    			"Paraigues": "Un paràigues? Qui collons necessita un paraigües? \nAi, que em sembla que estic començant a entendre per on van els tiros, i tu? \
Vols una pista de la meva hipòtesis? hahaha és broma, per la detectiva Marta això és bufar i fer peks.\
Va! Que ja només ens queda un objecte i es troba a la cuina, es troba a la cuina però per pura casualitat, sempre s’oblidava aquest tipus de coses per tot arreu.", 

    			"T10": "Alaa una T10! T’ha costat trobar-la? Vaia desendreçat no està fet, mira que oblidar-se-la a la cuina… \
Desendreçat i despistat, perquè allà on ha anat necessita una T10. Ja saps on és? Acostuma a agafar el metro.\
Ara que ja sé a on ha anat i perquè estic força més tranquil! Gràcies per tot superDetectiva! Quan sàpigues que ha passat \
escriu “/” + el lloc, i t’acabaré d’aclarir els dubtes extraoficialment. De mentres vaig a pintar, ballar i cantar amb els meus amics. Later!"}

    prediction, confidence = pred.predict_telegram(image_input_path)
    print(prediction, confidence)
    if confidence >= 0.65:
        if prediction in objectes.keys():
    	    update.message.reply_text(objectes[prediction])
        else:
            update.message.reply_text("Ai mira quin/a {} més maco/a".format(prediction))
    else:
    	update.message.reply_text("No em sona aquest objecte, potser no l'estic veient bé, prova de posar-lo amb un fons blanc.")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    #Dialogflow configuration
    
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(open('../token2.txt').read()[:-1], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("paris", paris))
    dp.add_handler(CommandHandler("VeureRegal", VeureRegal))

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
