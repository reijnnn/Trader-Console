from flask import flash
from ..extensions import logger, db
from ..telegram_bot.notifications_service import add_notification
from ..utils.helper import wrap_code, unwrap_code, escape_text
from ..trader_bot.strategies import (
    Alert,
    Price,
    Volume,
    Envelope,
    DumpPriceHistory,
    StrategyType,
)
from ..trader_bot.check_functions import CheckFunctions
from .models import Tasks, TaskStatus
from .tasks_service import get_task
from json import loads, dumps


class Task:
    def __init__(self, cmd, chat_id, reply_to_message_id=None, from_ui=False):

        self.chat_id = chat_id
        self.reply_to_message_id = reply_to_message_id
        self.from_ui = from_ui
        self.option = None
        self.strategy = None
        self.params = None

        self.config = {
            'entity': [
                'task'
            ],
            'options': [
                'help',
                'make',
                'list',
                'create',
                'cancel',
                'edit',
                'display'
            ],
            'help': [
                '/task [option] [params]'
            ],
            'examples': [
                '/task help',
                '/task help strategy=[strategy]',
                '/task make',
                '/task make strategy=[strategy]',
                '/task list',
                '/task list strategy=[strategy]',
                '/task display id=[id]',
                '/task cancel id=[id]',
                '/task create strategy=[strategy] par1=val1 ...',
                '/task edit id=[id] par1=val1 ...'
            ],
            'strategies': {
            }
        }

        self.config['strategies'][StrategyType.ALERT] = Alert.get_config()
        self.config['strategies'][StrategyType.ENVELOPE] = Envelope.get_config()
        self.config['strategies'][StrategyType.PRICE] = Price.get_config()
        self.config['strategies'][StrategyType.VOLUME] = Volume.get_config()
        self.config['strategies'][StrategyType.DUMP_PRICE_HISTORY] = DumpPriceHistory.get_config()

        self.parse_command(cmd)

    def create(self):
        required_params = self.config['strategies'][self.strategy]['params']
        required_params = [param for param in required_params if 'required' in required_params[param]]

        for param in required_params:
            if param not in self.params:
                msg = 'Strategy "{}" has required [params]:'.format(self.strategy) + "\n\n" + \
                      wrap_code('\n'.join(required_params))
                self.add_task_notification(text=msg)
                return

        default_params = self.config['strategies'][self.strategy]['params']
        default_params = [param for param in default_params if 'default' in default_params[param]]

        dump_params = {}
        for param in default_params:
            dump_params[param] = self.config['strategies'][self.strategy]['params'][param]['default']

        for param in self.params:
            dump_params[param] = self.params[param]

        task = Tasks(
            task_name=self.strategy,
            task_params=dumps(dump_params),
            task_status=TaskStatus.ACTIVE,
            chat_id=self.chat_id,
            reply_to_message_id=self.reply_to_message_id
        )
        db.session.add(task)
        db.session.commit()

        msg = 'Task with id={} created'.format(task.task_id)
        logger.debug(msg)

        self.add_task_notification(text=msg, task_id=task.task_id)

    def cancel(self):
        task_id = self.params['id']
        db.session.query(Tasks).filter_by(task_id=task_id, chat_id=self.chat_id).update(
            dict(task_status=TaskStatus.CANCELED))
        db.session.commit()

        msg = 'Task with id={} canceled'.format(task_id)
        logger.debug(msg)

        self.add_task_notification(text=msg, task_id=task_id)

    def edit(self):
        task_id = self.params['id']
        task = db.session.query(Tasks).filter_by(task_id=task_id, chat_id=self.chat_id).first()

        task_params = loads(task.task_params)

        for param_key, param_val in self.params.items():
            task_params[param_key] = param_val

        task.task_params = dumps(task_params)
        db.session.commit()

        msg = 'Task with id={} edited'.format(task_id)
        logger.debug(msg)

        self.add_task_notification(text=msg, task_id=task_id)

    def display(self):
        task_id = self.params['id']
        task = db.session.query(Tasks).filter_by(task_id=task_id, chat_id=self.chat_id).first()

        task_params = self.json_formatter(loads(task.task_params))
        task_params = escape_text(task_params)

        msg = 'Task "{}" with id={}'.format(task.task_name, task.task_id) + "\n\n" + \
              wrap_code('Params: {}'.format(task_params)) + "\n" + \
              wrap_code('Status: {}'.format(task.task_status)) + "\n" + \
              wrap_code('Date: {}'.format(task.task_date))
        logger.debug(msg)

        self.add_task_notification(text=msg, task_id=task_id)

    def list(self, strategy=None):
        query = db.session.query(Tasks).filter_by(task_status=TaskStatus.ACTIVE, chat_id=self.chat_id)
        if strategy:
            query = query.filter_by(task_name=strategy)

        active_tasks = query.all()

        if not active_tasks:
            msg = "Active tasks not found"
        else:
            msg = 'Active tasks:\n\n'
            for task in active_tasks:
                msg += 'Task "{}" with id={}\n'.format(task.task_name, task.task_id)

        logger.debug(msg)

        self.add_task_notification(text=msg)

    def help(self, strategy=None):
        if strategy:
            params = self.config['strategies'][strategy]['params']
            required_params = [param for param in params if 'required' in params[param]]
            optional_params = [param for param in params if 'required' not in params[param]]
            examples = self.config['strategies'][strategy]['help']['examples']

            self.add_task_notification(text='Command examples:' + "\n" +
                                            wrap_code(escape_text('\n'.join(examples))) + "\n\n" +
                                            'Required [params]:' + "\n" +
                                            wrap_code('\n'.join(required_params)) + "\n\n" +
                                            'Optional [params]:' + "\n" +
                                            wrap_code('\n'.join(optional_params)))
        else:
            self.add_task_notification(text='Command format:' + "\n" +
                                            wrap_code(' '.join(self.config['help'])) + "\n\n" +
                                            '[option]:' + "\n" +
                                            wrap_code('\n'.join(self.config['options'])) + "\n\n" +
                                            '[params]:' + "\n" +
                                            'Individually for every strategy' + "\n" +
                                            'More info:' + "\n" +
                                            wrap_code('/task help strategy=[strategy]') + "\n" +
                                            wrap_code('/task make strategy=[strategy]') + "\n\n" +
                                            '[strategy]:' + "\n" +
                                            wrap_code('\n'.join(self.config['strategies'])) + "\n\n" +
                                            'Examples:' + "\n" +
                                            wrap_code('\n'.join(self.config['examples'])))

    def make(self, strategy=None):
        make_list = []
        if strategy:
            params = self.config['strategies'][strategy]['params']

            make_list.append('create')
            for param in params:

                if param == 'id':
                    continue

                if param == 'strategy':
                    make_list.append('strategy={}'.format(strategy))
                    continue

                if 'default' in params[param]:
                    make_list.append('{}={}'.format(param, params[param]['default']))
                else:
                    make_list.append('{}=[*]'.format(param))
        else:
            make_list.append('make')
            make_list.append('strategy=[*]')

        self.add_task_notification(text=wrap_code('/task ' + ' '.join(make_list)))

    def json_formatter(self, params):
        res = "{ " + "\n"
        for k, v in params.items():
            res += '"{}": {}\n'.format(k, v)
        res += "}"
        return res

    def parse_params(self, params):
        error_stack = []
        for param_key, param_val in params.items():
            if param_key not in self.config['strategies'][self.strategy]['params']:
                error_stack.append('Parameter "{}" is not supported'.format(param_key))
            elif param_key == '' or param_val == '':
                error_stack.append(
                    'In pair "{}={}" [key=val] one of the elements is empty'.format(param_key, param_val))
        return error_stack

    def call_check_functions(self, params):
        error_stack = []
        for param_key, param_val in params.items():
            if 'check_function' in self.config['strategies'][self.strategy]['params'][param_key]:
                function_name = self.config['strategies'][self.strategy]['params'][param_key]['check_function']
                if not getattr(CheckFunctions, function_name)(param_val):
                    error_stack.append('Incorrect value={} for param "{}"'.format(param_val, param_key))
        return error_stack

    def convert_params(self, params):
        o_params = {}
        for param in params:
            pair = param.split('=')
            if len(pair) == 1:
                o_params[pair[0]] = ''
            else:
                o_params[pair[0]] = pair[1]
        return o_params

    def trim_cmd(self, cmd):

        cmd_length = len(cmd)
        while True:
            cmd = cmd.replace('  ', ' ')
            if len(cmd) == cmd_length:
                break
            cmd_length = len(cmd)

        cmd = cmd.replace('= ', '=')
        cmd = cmd.replace(' =', '=')
        cmd = cmd.strip()

        return cmd

    def parse_command(self, cmd):
        cmd = self.trim_cmd(cmd)
        cmd = cmd.split(' ')

        if cmd[0].strip('/') not in self.config['entity']:
            return

        if len(cmd) == 1:
            self.help()
            return

        self.option = cmd[1]

        if self.option not in self.config['options']:
            self.add_task_notification(text='Option "{}" is not supported'.format(self.option))
            return

        if len(cmd) == 2:
            if self.option == 'list':
                self.list()
            elif self.option == 'make':
                self.make()
            else:
                self.help()
            return

        self.params = self.convert_params(cmd[2:])

        if self.option in ['cancel', 'edit', 'display'] and 'id' not in self.params:
            self.add_task_notification(text='This operation requires parameter "id="')
            return

        if self.option in ['cancel', 'edit', 'display'] and not self.find_task():
            self.add_task_notification(text="Task with id={} not found in this chat".format(self.params['id']))
            return

        if 'strategy' in self.params and self.params['strategy'] not in self.config['strategies']:
            self.add_task_notification(text='Strategy "{}" is not supported'.format(self.params['strategy']))
            return

        if self.option in ['create'] and 'strategy' not in self.params:
            self.add_task_notification(text='This operation requires parameter "strategy="')
            return

        if 'strategy' in self.params:
            self.strategy = self.params['strategy']

        if self.option in ['cancel', 'edit', 'display']:
            task = get_task(self.params['id'])
            self.strategy = task.task_name

        if self.strategy is None and self.option in ['list', 'help', 'make']:
            self.add_task_notification(text='Incorrect [params]:' + "\n" +
                                            wrap_code('\n'.join(self.params)) + "\n\n" +
                                            'Available [params]:' + "\n" +
                                            wrap_code('strategy'))
            return

        error_stack = self.parse_params(self.params)
        if len(error_stack):
            strategy_params = [param for param in self.config['strategies'][self.strategy]['params']]
            self.add_task_notification(text='Incorrect [params]:' + "\n" +
                                            wrap_code('\n'.join(error_stack)) + "\n\n" +
                                            'Available [params]:' + "\n" +
                                            wrap_code('\n'.join(strategy_params)))
            return

        error_stack = self.call_check_functions(self.params)
        if len(error_stack):
            self.add_task_notification(text='Incorrect [params] value:' + "\n\n" +
                                            wrap_code('\n'.join(error_stack)))
            return

        if self.option == 'help':
            self.help(self.strategy)
        if self.option == 'list':
            self.list(self.strategy)
        if self.option == 'make':
            self.make(self.strategy)
        if self.option == 'create':
            self.create()
        if self.option == 'cancel':
            self.cancel()
        if self.option == 'edit':
            self.edit()
        if self.option == 'display':
            self.display()

    def find_task(self):
        task = db.session.query(Tasks).filter_by(task_id=self.params['id'], chat_id=self.chat_id).first()
        if not task:
            return False
        return True

    def add_task_notification(self, text, task_id=''):
        if self.from_ui:
            flash(unwrap_code(text), 'info')
        else:
            add_notification(text=text, chat_id=self.chat_id, task_id=task_id, reply_to_message_id=self.reply_to_message_id)
