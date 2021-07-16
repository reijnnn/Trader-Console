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
from .strategies import (
    Alert,
    Price,
    Volume,
    Envelope,
    DumpPriceHistory,
    StrategyType,
)


class TraderBot(threading.Thread):

    def __init__(self, app=None):
        super(TraderBot, self).__init__()
        self.is_active = False
        self.app = None

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
                            if task.task_name == StrategyType.ALERT:
                                strategy = Alert(api=binance_api)
                                strategy.execute(task.task_id)
                            if task.task_name == StrategyType.ENVELOPE:
                                strategy = Envelope(api=binance_api)
                                strategy.execute(task.task_id)
                            if task.task_name == StrategyType.PRICE:
                                strategy = Price(api=binance_api)
                                strategy.execute(task.task_id)
                            if task.task_name == StrategyType.VOLUME:
                                strategy = Volume(api=binance_api)
                                strategy.execute(task.task_id)
                            if task.task_name == StrategyType.DUMP_PRICE_HISTORY:
                                strategy = DumpPriceHistory(api=binance_api)
                                strategy.execute(task.task_id)

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
