from datetime import datetime
from json import loads

# noinspection PyPackageRequirements
from sqlalchemy import desc

from ...extensions import db
from ...task.tasks_service import get_task, complete_task
from ...telegram_bot.notifications_service import add_notification
from ...utils.helper import wrap_code
from ..indicators import moving_average_envelope, stochrsi
from ..models import BinanceKlines
from .strategy import Strategy


class Envelope(Strategy):

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
                'calc_period': {
                    'default': 20,
                    'check_function': 'check_calc_period'
                },
                'channels_env_percentage': {
                    'default': '4,9,14',
                    'check_function': 'check_comma_separated_ints'
                },
                'cross_channel_lvl': {
                    'required': 1,
                    'check_function': 'check_channel_lvl'
                },

                'period': {
                    'default': '3m',
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
                    '/task help strategy=envelope',
                    '/task list strategy=envelope',
                    '/task create strategy=envelope symbol=BTCUSDT interval=5m cross_channel_lvl=-1',
                    '/task cancel id=[id]',
                    '/task display id=[id]',
                    '/task edit id=[id] period=1m duration=1w',
                    '/task edit id=[id] channels_env_percentage=3,8,12'
                ]
            }
        }
        return config

    def execute(self, task_id):
        task = get_task(task_id)
        params = loads(task.task_params)

        period = int(params['calc_period'])
        symbol = params['symbol']
        interval = params['interval']
        channels_env_percentage = params['channels_env_percentage']
        cross_channel_lvl = int(params['cross_channel_lvl'])

        is_actual_klines = self.load_klines(symbol=symbol, interval=interval)
        if not is_actual_klines:
            return

        klines = db.session.query(BinanceKlines). \
            filter_by(symbol=symbol, interval=interval). \
            order_by(desc(BinanceKlines.open_time)). \
            limit(period * 3). \
            offset(0). \
            all()

        curr_price = float(klines[0].close)
        curr_time = datetime.fromtimestamp(float(klines[0].open_time) / 1000).strftime('%Y-%m-%d %H:%M:%S')

        klines = [float(kline.close) for kline in klines]
        klines = klines[::-1]

        channels_env = channels_env_percentage.split(',')
        channel_num = 0
        for channel in channels_env:
            lb, cb, ub = moving_average_envelope(klines, period, int(channel) / 100)
            stoch_rsi = stochrsi(klines, period)

            if abs(cross_channel_lvl) == channel_num + 1:

                if cross_channel_lvl < 0 and lb[-1] > curr_price or \
                        cross_channel_lvl > 0 and ub[-1] < curr_price:
                    notif_text = ("Task with id={} completed." + "\n\n" +
                                  wrap_code("Time: {}" + "\n" +
                                            "Symbol: {}" + "\n" +
                                            "Interval: {}" + "\n" +
                                            "Price: {}" + "\n" +
                                            "Channel level: {}" + "\n" +
                                            "Stoch RSI: {}" + "\n" +
                                            "Envelope: {}, {}, {}")
                                  ).format(
                        task.task_id,
                        curr_time,
                        symbol,
                        interval,
                        round(curr_price, 3),
                        cross_channel_lvl,
                        round(stoch_rsi[-1], 3),
                        round(lb[-1], 3), round(cb[-1], 3), round(ub[-1], 3)
                    )
                    complete_task(task_id)
                    add_notification(text=notif_text,
                                     chat_id=task.chat_id,
                                     task_id=task.task_id,
                                     reply_to_message_id=task.reply_to_message_id)
                break
            channel_num += 1
