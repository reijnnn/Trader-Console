from os import path
# from string import ascii_letters, digits
# from random import choice

APP_NAME = 'Trader Console'
ENV = 'DEV'
DEBUG = True
HOST = '127.0.0.1'
PORT = 8085
DOMAIN_NAME = 'DOMAIN_NAME'

JSON_SORT_KEYS = False

# ''.join([choice(ascii_letters + digits) for n in range(64)])
SECRET_KEY = 'RANDOM_SECRET_KEY'
WTF_CSRF_SECRET_KEY = 'RANDOM_WTF_CSRF_SECRET_KEY'

REMEMBER_COOKIE_DURATION = 24 * 60 * 60

INSTANCE_DIR = path.join(path.dirname(path.dirname(__file__)), 'instance_default')

MIGRATIONS_DIR = path.join(INSTANCE_DIR, 'migrations')

APP_LOG_DEBUG_FILE = path.join(INSTANCE_DIR, 'logs', 'debug.log')
APP_LOG_INFO_FILE = path.join(INSTANCE_DIR, 'logs', 'info.log')
APP_LOG_ERROR_FILE = path.join(INSTANCE_DIR, 'logs', 'error.log')
APP_LOG_MAX_BYTES = 1024 * 1024
APP_LOG_BACKUP_COUNT = 3
APP_LOG_MSG_FORMAT = '[%(asctime)s]: %(message)s'
APP_LOG_DATETIME_FORMAT = '%m/%d/%Y %H:%M:%S'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(INSTANCE_DIR, 'sqlite3', 'sqlite3.db') + '?check_same_thread=False'
SQLALCHEMY_TRACK_MODIFICATIONS = False

PAGINATION_PAGE_SIZE = 30

TELEGRAM_BOT_ENABLED = False
TELEGRAM_BOT_NAME = 'BOT_NAME'
TELEGRAM_BOT_TOKEN = 'BOT_TOKEN'
TELEGRAM_BOT_PATH = 'https://api.telegram.org/bot'
TELEGRAM_BOT_POLLING_FREQ = 10
TELEGRAM_BOT_PROXY = {}
TELEGRAM_BOT_TIMEOUT = 5
TELEGRAM_ADMIN_USERNAME = 'YOUR_USERNAME'

PROXY_BOT_ENABLED = False
PROXY_BOT_CHECK_PATH = 'https://api.telegram.org/bot'
PROXY_BOT_TIMEOUT = 3
PROXY_BOT_POLLING_FREQ = 10
PROXY_BOT_CNT_TOP_PROXY = 15

TRADER_BOT_ENABLED = False
TRADER_BOT_POLLING_FREQ = 10
BINANCE_API_KEY = 'BINANCE_API_KEY'
BINANCE_SECRET_KEY = 'BINANCE_SECRET_KEY'

COUNT_MAX_TASK_ERRORS = 10
