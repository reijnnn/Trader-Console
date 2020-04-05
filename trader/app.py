import logging
from os import path, makedirs

from logging.handlers import RotatingFileHandler
from flask            import Flask
from .extensions      import (
   login_manager,
   csrf,
   migrate,
   logger,
   db,
   trader_bot,
   proxy_bot,
   telegram_bot
)

__all__ = ("create_app")

def create_app(config=None):
   app = Flask(__name__)

   if config is None:
      config = "config.py"

   app.config.from_pyfile(config)

   configure_app_structure(app)
   configure_logging(app)
   configure_extensions(app)
   configure_threads(app)
   configure_blueprints(app)
   configure_jinja(app)

   logger.info('"{}" application started with config "{}"'.format(app.config['APP_NAME'], config))

   return app

def configure_app_structure(app):
   makedirs(app.config['INSTANCE_DIR'],                       exist_ok=True)
   makedirs(path.join(app.config['INSTANCE_DIR'], 'logs'),    exist_ok=True)
   makedirs(path.join(app.config['INSTANCE_DIR'], 'sqlite3'), exist_ok=True)

def configure_threads(app):
   trader_bot.init_app(app)
   if app.config['TRADER_BOT_ENABLED']:
      trader_bot.start()

   proxy_bot.init_app(app)
   if app.config['PROXY_BOT_ENABLED']:
      proxy_bot.start()

   telegram_bot.init_app(app)
   if app.config['TELEGRAM_BOT_ENABLED']:
      telegram_bot.start()

def configure_extensions(app):
   db.init_app(app)
   db.set_app_instance(app)
   login_manager.init_app(app)
   csrf.init_app(app)
   migrate.init_app(app, db, app.config['MIGRATION_DIR'])

def configure_blueprints(app):
   from .frontend.views     import frontend_bp
   from .user.views         import user_bp
   from .task.views         import task_bp
   from .sql.views          import sql_bp
   from .trader_bot.views   import trader_bot_bp
   from .telegram_bot.views import telegram_bot_bp
   from .proxy_bot.views    import proxy_bot_bp

   app.register_blueprint(frontend_bp)
   app.register_blueprint(user_bp)
   app.register_blueprint(task_bp)
   app.register_blueprint(sql_bp)
   app.register_blueprint(trader_bot_bp)
   app.register_blueprint(telegram_bot_bp)
   app.register_blueprint(proxy_bot_bp)

def configure_logging(app):
   error_log_handler = RotatingFileHandler(app.config['APP_LOG_ERROR_FILE'], maxBytes=app.config['APP_LOG_MAX_BYTES'], backupCount=app.config['APP_LOG_BACKUP_COUNT'])
   error_log_handler.setFormatter(logging.Formatter(app.config['APP_LOG_MSG_FORMAT'], app.config['APP_LOG_DATETIME_FORMAT']))
   error_log_handler.setLevel(logging.ERROR)
   logger.addHandler(error_log_handler)

   info_log_handler = RotatingFileHandler(app.config['APP_LOG_INFO_FILE'], maxBytes=app.config['APP_LOG_MAX_BYTES'], backupCount=app.config['APP_LOG_BACKUP_COUNT'])
   info_log_handler.setFormatter(logging.Formatter(app.config['APP_LOG_MSG_FORMAT'], app.config['APP_LOG_DATETIME_FORMAT']))
   info_log_handler.setLevel(logging.INFO)
   logger.addHandler(info_log_handler)

   debug_log_handler = RotatingFileHandler(app.config['APP_LOG_DEBUG_FILE'], maxBytes=app.config['APP_LOG_MAX_BYTES'], backupCount=app.config['APP_LOG_BACKUP_COUNT'])
   debug_log_handler.setFormatter(logging.Formatter(app.config['APP_LOG_MSG_FORMAT'], app.config['APP_LOG_DATETIME_FORMAT']))
   debug_log_handler.setLevel(logging.DEBUG)
   logger.addHandler(debug_log_handler)

   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger("urllib3").setLevel(logging.WARNING)

def configure_jinja(app):
   from .utils.pagination import url_for_other_page, url_for_search
   from .utils.helper     import get_app_name, get_telegram_admin_username
   app.jinja_env.globals['url_for_other_page']          = url_for_other_page
   app.jinja_env.globals['url_for_search']              = url_for_search
   app.jinja_env.globals['get_app_name']                = get_app_name
   app.jinja_env.globals['get_telegram_admin_username'] = get_telegram_admin_username
