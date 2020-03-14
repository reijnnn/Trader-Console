from trader.utils.database import SQLAlchemyDB
db = SQLAlchemyDB()

from flask_migrate import Migrate
migrate = Migrate()

from flask_wtf.csrf  import CSRFProtect
csrf = CSRFProtect()

from flask_login import LoginManager
login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'info'

import logging
logger = logging.getLogger('application.logger')

from trader.proxy_bot.proxy_bot import Proxy_bot
proxy_bot = Proxy_bot()

from trader.telegram_bot.telegram_bot import Telegram_bot
telegram_bot = Telegram_bot()

from trader.trader_bot.trader_bot import Trader_bot
trader_bot = Trader_bot()
