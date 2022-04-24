from datetime import datetime
from json import loads

# noinspection PyPackageRequirements
from sqlalchemy import desc

from ...extensions import db
from ...task.tasks_service import get_task, complete_task
from ...telegram_bot.notifications_service import add_notification
from ...utils.helper import wrap_code

from ..models import BinanceKlines
from .strategy import Strategy


class Volume(Strategy):

    @staticmethod
    def get_config():
        config = {
            'params': {
                'strategy': {
                    'required': 1
                },

                'symbol': {
                    'required': 1,
                    'check_function': 'check_symbol'
                },
                'interval': {
                    'required': 1,
                    'check_function': 'check_interval'
                },
                'change_percentage': {
                    'default': 1.2,
                    'check_function': 'check_percentage'
                },

                'period': {
                    'default': '2m',
                    'check_function': 'check_period'
                },
                'duration': {
                    'default': '1M',
                    'check_function': 'check_duration'
                },
                'id': {
                }
            },
            'help': {
                'examples': [
                    '/task create strategy=volume symbol=ETHUSDT interval=1h',
                    '/task edit id=[id] period=1m duration=1w'
                ]
            }
        }
        return config

    def execute(self, task_id):
        task = get_task(task_id)
        params = loads(task.task_params)

        is_actual_klines = self.load_klines(symbol=params['symbol'], interval=params['interval'], limit=12)
        if not is_actual_klines:
            return

        klines = db.session.query(BinanceKlines). \
            filter_by(symbol=params['symbol'], interval=params['interval']). \
            order_by(desc(BinanceKlines.open_time)). \
            limit(1). \
            all()

        curr_time = datetime.fromtimestamp(float(klines[0].open_time) / 1000).strftime('%Y-%m-%d %H:%M:%S')
        open_price = float(klines[0].open)
        close_price = float(klines[0].close)

        if abs((open_price - close_price) / open_price * 100) > float(params['change_percentage']):
            notif_text = ('Task "volume" with id={} completed. ' + "\n\n" +
                          wrap_code("Time: {}" + "\n" +
                                    "Symbol: {}" + "\n" +
                                    "Interval: {}" + "\n" +
                                    "Price: {}")
                          ).format(
                task.task_id,
                curr_time,
                params['symbol'],
                params['interval'],
                round(close_price, 3)
            )

            complete_task(task.task_id)
            add_notification(text=notif_text,
                             chat_id=task.chat_id,
                             task_id=task.task_id,
                             reply_to_message_id=task.reply_to_message_id)
