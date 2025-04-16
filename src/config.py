from os import getenv

from dotenv import load_dotenv


load_dotenv()


# Telegram Bot configuration
BOT_TOKEN = getenv('TOKEN', '')
BOT_MSG_PARSE_MODE = 'MarkdownV2'

# MongoDB configuration
MONGO_DSN = getenv('MONGO_DSN', 'mongodb://localhost:27017')
MONGO_DB_NAME = 'helper'
