from ..extensions import logger, proxy_bot
from ..task.task import Task
from ..user.users_service import get_telegram_users
from ..proxy_bot.proxies_service import get_proxy
from .notifications_service import get_queue_notifications, update_notification_status
import requests
from requests.exceptions import Timeout, ProxyError, SSLError
import threading
import time


class TelegramBot(threading.Thread):
    def __init__(self, app=None):
        super(TelegramBot, self).__init__()
        self.offset = 0
        self.is_active = False

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def restart(self):
        self.is_active = True
        logger.info("Telegram bot started")

    def cancel(self):
        self.is_active = False
        logger.info("Telegram bot stopped")

    def get_status(self):
        return 'active' if self.is_active else 'inactive'

    def get_thread_status(self):
        return 'active' if self.is_alive() else 'inactive'

    def refresh_proxy(self):
        if proxy_bot.get_status() == 'inactive':
            self.app.config['TELEGRAM_BOT_PROXY'] = {}
            return True

        active_proxy_id = proxy_bot.get_active_proxy_id()
        if not active_proxy_id:
            return False

        active_proxy = get_proxy(active_proxy_id)
        if not active_proxy:
            return False

        self.app.config['TELEGRAM_BOT_PROXY'] = active_proxy.get_object_format()

        return True

    def send_queue_notifications(self):
        queue_notifications = get_queue_notifications()

        for notification in queue_notifications:
            if self.send_message({'chat_id': notification.chat_id,
                                  'text': notification.notif_text,
                                  'reply_to_message_id': notification.reply_to_message_id,
                                  'disable_web_page_preview': True,
                                  'parse_mode': 'HTML'}):
                update_notification_status(notification.notif_id)

    def run(self):

        bot_desc = self.get_me()
        if bot_desc:
            logger.info("Telegram bot '{}' started".format(bot_desc['username']))
        else:
            logger.info("Telegram bot started")

        self.is_active = True
        while True:
            while self.is_active:

                if not self.refresh_proxy():
                    continue

                self.send_queue_notifications()

                try:
                    updates = self.get_updates(self.offset)
                    if updates is None:
                        time.sleep(self.app.config['TELEGRAM_BOT_POLLING_FREQ'])
                        continue

                    for update in updates['result']:
                        self.offset = update['update_id'] + 1

                        if not update.get('message'):
                            continue

                        if not update['message'].get('text'):
                            continue

                        if not update['message']['text'].startswith('/'):
                            continue

                        chat_id = update['message']['chat']['id']
                        reply_to_message_id = update['message']['message_id']

                        if update['message']['text'] == '/id':
                            self.send_message({'chat_id': chat_id,
                                               'text': 'Your id = "{}"'.format(chat_id)})
                            continue

                        if update['message']['text'] == '/start':
                            self.send_message({'chat_id': chat_id,
                                               'text': "Hi. I'm a bot." + "\n" +
                                                       "I'll help you." + "\n" +
                                                       "For more info use /help command."})

                        if update['message']['text'] == '/help':
                            self.send_message({'chat_id': chat_id,
                                               'text': "Available commands:" + "\n" +
                                                       "/id - to register in the system, "
                                                       "send command's result to admin" + "\n" +
                                                       "/ping - to check the bot" + "\n" +
                                                       "/task - to manage tasks"})
                            continue

                        if update['message']['text'] == '/ping':
                            self.send_message({'chat_id': chat_id,
                                               'text': 'pong'})
                            continue

                        telegram_users_list = get_telegram_users()

                        if chat_id not in telegram_users_list:
                            logger.info('Unknown user try to send msg: {}'.format(update['message']))
                            self.send_message({'chat_id': chat_id,
                                               'text': 'You are not authorized to access this bot'})
                            continue

                        Task(update['message']['text'], chat_id, reply_to_message_id)
                except Exception as e:
                    logger.error('Telegram bot. Error: {}'.format(e))

                time.sleep(self.app.config['TELEGRAM_BOT_POLLING_FREQ'])

    def get_me(self):
        try:
            with requests.get('{}{}/{}'.format(self.app.config['TELEGRAM_BOT_PATH'],
                                               self.app.config['TELEGRAM_BOT_TOKEN'],
                                               'getMe'),
                              proxies=self.app.config['TELEGRAM_BOT_PROXY'],
                              timeout=self.app.config['TELEGRAM_BOT_TIMEOUT']) as request:
                message = request.json()
                if not message.get('ok', False):
                    logger.error('Telegram bot. getMe. Unknown error')
                    return None
                return message['result']
        except (Timeout, ProxyError, SSLError):
            logger.debug('Telegram bot. getMe. Timeout')
            return None
        except Exception as e:
            logger.error('Telegram bot. getMe. Error: {}'.format(e))
            return None

    def get_updates(self, offset):
        try:
            with requests.get('{}{}/{}'.format(self.app.config['TELEGRAM_BOT_PATH'],
                                               self.app.config['TELEGRAM_BOT_TOKEN'],
                                               'getUpdates'),
                              params={'offset': offset},
                              proxies=self.app.config['TELEGRAM_BOT_PROXY'],
                              timeout=self.app.config['TELEGRAM_BOT_TIMEOUT']) as request:
                message = request.json()
                if not message.get('ok', False):
                    logger.error('Telegram bot. getUpdates. Unknown error')
                    return None
            return message
        except (Timeout, ProxyError, SSLError):
            logger.debug('Telegram bot. getUpdates. Timeout')
            return None
        except Exception as e:
            logger.error('Telegram bot. getUpdates. Error: {}'.format(e))
            return None

    def send_message(self, params):
        try:
            with requests.get('{}{}/{}'.format(self.app.config['TELEGRAM_BOT_PATH'],
                                               self.app.config['TELEGRAM_BOT_TOKEN'],
                                               'sendMessage'),
                              params=params,
                              proxies=self.app.config['TELEGRAM_BOT_PROXY'],
                              timeout=self.app.config['TELEGRAM_BOT_TIMEOUT']) as request:
                message = request.json()
                if not message.get('ok', False):
                    logger.error('Telegram bot. sendMessage. Unknown error')
                    return None
                return True
        except (Timeout, ProxyError, SSLError):
            logger.debug('Telegram bot. sendMessage. Timeout')
            return None
        except Exception as e:
            logger.error('Telegram bot. sendMessage. Error: {}'.format(e))
            return None
