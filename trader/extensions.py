from trader.utils.database import SQLAlchemyDB
db = SQLAlchemyDB()

from flask_migrate import Migrate
migrate = Migrate()

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()

from flask_login import LoginManager
login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'info'

import logging
logger = logging.getLogger('application.logger')

from trader.proxy_bot.proxy_bot import ProxyBot
proxy_bot = ProxyBot()

from trader.telegram_bot.telegram_bot import TelegramBot
telegram_bot = TelegramBot()

from trader.trader_bot.trader_bot import TraderBot
trader_bot = TraderBot()
