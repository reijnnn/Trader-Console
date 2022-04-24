from json import loads

from ...task.tasks_service import get_task, complete_task
from ...telegram_bot.notifications_service import add_notification
from ...utils.helper import wrap_code
from .strategy import Strategy


class Price(Strategy):

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
                    'default': '4h',
                    'check_function': 'check_interval'
                },

                'id': {
                }
            },
            'help': {
                'examples': [
                    '/task create strategy=price symbol=ETHUSDT',
                    '/task create strategy=price symbol=ETHUSDT interval=1h'
                ]
            }
        }
        return config

    def execute(self, task_id):
        task = get_task(task_id)
        params = loads(task.task_params)

        kline = self.load_last_kline(params['symbol'], params['interval'])
        complete_task(task_id)
        add_notification(text=('Task "price" with id={} completed. ' + "\n\n" +
                               wrap_code('Symbol: {}' + "\n" +
                                         'Interval: {}' + "\n" +
                                         'Current price: {}' + "\n" +
                                         'Low price: {}' + "\n" +
                                         'High price: {}' + "\n" +
                                         'Count trades: {}')
                               ).format(
            task_id,
            params['symbol'],
            kline.interval,
            float(kline.close),
            float(kline.low),
            float(kline.high),
            kline.num_trades),
            chat_id=task.chat_id,
            task_id=task.task_id,
            reply_to_message_id=task.reply_to_message_id)
