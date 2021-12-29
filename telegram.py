""" Functions related to the Telegram bot """
from logging.handlers import RotatingFileHandler
import sys
import logging
from os import environ
import requests
from dotenv import load_dotenv
from utils import exception_info

logging.basicConfig(handlers=[RotatingFileHandler('data/log.txt', maxBytes=524288, backupCount=10)],
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)

load_dotenv('config.cfg')
BOT_TOKEN = environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = environ.get('TELEGRAM_CHAT_ID')


def telegram_bot_sendtext(bot_message):
    """
        Function to send text messages to a telegram bot
    Args:
        bot_message (str): message you want to send to the bot
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&parse_mode=HTML&text={bot_message}"
    try:
        response = requests.get(url).json()
        LOGGER.info(f"Telegram message status: {response['ok']}")
    except requests.exceptions.RequestException:
        LOGGER.error(exception_info(sys.exc_info()))
        sys.exit(1)
