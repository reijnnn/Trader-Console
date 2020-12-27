import time
import threading
from ..extensions import logger
from ..task.tasks_service import (
    get_active_tasks,
    add_task_error,
    get_task_errors,
    need_execute_task,
    update_task_exec_time,
    need_end_task,
    end_task,
)
from ..utils.helper import wrap_code, escape_text
from ..telegram_bot.notifications_service import add_notification
from .binance_api import BinanceApi
from .strategies import Strategies


class TraderBot(threading.Thread):

    def __init__(self, app=None):
        super(TraderBot, self).__init__()
        self.is_active = False

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def run(self):

        logger.info("Trader bot started")

        self.is_active = True
        while True:
            while self.is_active:
                binance_api = BinanceApi(self.app.config['BINANCE_API_KEY'], self.app.config['BINANCE_SECRET_KEY'])

                res, err = binance_api.ping()
                if err:
                    logger.debug('Trader bot. API ping. Timeout')
                    time.sleep(self.app.config['TRADER_BOT_POLLING_FREQ'])
                    continue

                active_tasks = get_active_tasks()
                if active_tasks:
                    for task in active_tasks:

                        if need_end_task(task.task_id):
                            end_task(task.task_id)
                            add_notification(text=('Your task with id={} was ended.' + "\n" +
                                                   'Duration is expired').format(task.task_id),
                                             chat_id=task.chat_id,
                                             task_id=task.task_id,
                                             reply_to_message_id=task.reply_to_message_id)
                            continue

                        if not need_execute_task(task.task_id):
                            continue

                        try:
                            call_strategy = Strategies(api=binance_api)

                            if task.task_name == 'alert':
                                call_strategy.strategy_alert(task.task_id)
                            if task.task_name == 'envelope':
                                call_strategy.strategy_envelope(task.task_id)
                            if task.task_name == 'price':
                                call_strategy.strategy_price(task.task_id)
                            if task.task_name == 'volume':
                                call_strategy.strategy_volume(task.task_id)
                            if task.task_name == 'dump_price_history':
                                call_strategy.strategy_dump_price_history(task.task_id)

                            update_task_exec_time(task.task_id)
                        except Exception as e:
                            logger.error('Trader bot. Error: {}'.format(e))

                            add_task_error(task.task_id)

                            if get_task_errors(task.task_id) == self.app.config['COUNT_MAX_TASK_ERRORS']:
                                add_notification(text=('Your task with id={} has many errors.' + "\n\n" +
                                                       wrap_code('Last error: {}')).format(task.task_id,
                                                                                           escape_text(str(e))),
                                                 chat_id=task.chat_id,
                                                 task_id=task.task_id,
                                                 reply_to_message_id=task.reply_to_message_id)

                        time.sleep(self.app.config['TRADER_BOT_POLLING_FREQ'])

    def restart(self):
        self.is_active = True
        logger.info("Trader bot started")

    def cancel(self):
        self.is_active = False
        logger.info("Trader bot stopped")

    def get_status(self):
        return 'active' if self.is_active else 'inactive'

    def get_thread_status(self):
        return 'active' if self.is_alive() else 'inactive'
