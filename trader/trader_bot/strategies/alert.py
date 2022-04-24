from json import loads

from ...task.tasks_service import get_task, complete_task
from ...telegram_bot.notifications_service import add_notification
from ...utils.helper import wrap_code
from .strategy import Strategy


class Alert(Strategy):

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
                'condition': {
                    'required': 1,
                    'check_function': 'check_condition'
                },
                'price': {
                    'required': 1,
                    'check_function': 'check_price'
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
                    '/task help strategy=alert',
                    '/task list strategy=alert',
                    '/task create strategy=alert symbol=ETHUSDT condition=< price=180',
                    '/task cancel id=[id]',
                    '/task display id=[id]',
                    '/task edit id=[id] price=190',
                    '/task edit id=[id] period=1m duration=1w'
                ]
            }
        }
        return config

    def execute(self, task_id):
        task = get_task(task_id)
        params = loads(task.task_params)

        curr_price = self.load_price(params['symbol'])

        if params['condition'] == '>' and float(curr_price) > float(params['price']) or \
                params['condition'] == '<' and float(curr_price) < float(params['price']):
            complete_task(task_id)
            add_notification(text=('Task "alert" with id={} completed.' + "\n\n" +
                                   wrap_code('Price: {}')
                                   ).format(task_id, float(curr_price)),
                             chat_id=task.chat_id,
                             task_id=task.task_id,
                             reply_to_message_id=task.reply_to_message_id)
