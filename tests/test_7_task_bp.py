from tests.base_test_case import BaseTestCase
from flask import url_for
from trader.task.models import Tasks, TaskStatus
from trader.task.task import Task
from trader.telegram_bot.models import Notifications
from json import loads


class TestTaskBP(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls._init_app(cls)
        cls._init_db(cls)
        cls._print_test_desc(cls, __name__)

    def setUp(self):
        self._logout()
        self.db.session.query(Tasks).delete()
        self.db.session.query(Notifications).delete()

    def tearDown(self):
        pass

    def test_access(self):
        with self.app.test_request_context():
            # monitor_tasks.GET
            page = self.client.get(url_for('task.monitor_tasks'), follow_redirects=False)
            self.assertEqual(page.status_code, 302)

            task = self._create_task()
            self.assertEqual(task.task_status, TaskStatus.ACTIVE)

            # cancel_active_task.GET
            self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
            self.assertNotEqual(task.task_status, TaskStatus.CANCELED)

            self.db.session.delete(task)

            # get_config_task.GET
            task_config = self.client.get(url_for('task.get_config_task', task_name='alert'), follow_redirects=False)
            self.assertEqual(task_config.status_code, 302)

            self._create_task(
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": "<",
                    "price": "110"
                }"""
            )

            self.assertEqual(self._get_tasks_count(), 1)

            user = self._create_new_user(telegram_id=self.COMMON_TELEGRAM_ID)

            # create_task.POST
            self.client.post(url_for('task.create_task'), data=dict(
                task_id=None,
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": ">",
                    "price": "1000"
                }""",
                user=user.id
            ), follow_redirects=False)

            self.assertEqual(self._get_tasks_count(), 1)

            task = self.db.session.query(Tasks).first()

            # edit_task.POST
            self.client.post(url_for('task.edit_task'), data=dict(
                task_id=task.task_id,
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": ">",
                    "price": "1111"
                }""",
                user=user.id
            ), follow_redirects=False)

            task = self.db.session.query(Tasks).first()
            task_params = loads(task.task_params)
            self.assertEqual(int(task_params['price']), 110)

    def test_super_admin(self):
        self._create_super_admin()
        self._login(self.SUPER_ADMIN_LOGIN, self.SUPER_ADMIN_PASSWORD)

        with self.app.test_request_context():
            # monitor_tasks.GET
            page = self.client.get(url_for('task.monitor_tasks'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            task = self._create_task()
            self.assertEqual(task.task_status, TaskStatus.ACTIVE)

            # cancel_active_task.GET
            self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
            self.assertEqual(task.task_status, TaskStatus.CANCELED)

            # get_config_task.GET
            task_config = self.client.get(url_for('task.get_config_task', task_name='alert'), follow_redirects=False)
            self.assertEqual(task_config.status_code, 200)

            user = self._get_user_by_login(self.SUPER_ADMIN_LOGIN)
            self._edit_exist_user(user_id=user.id, telegram_id=self.COMMON_TELEGRAM_ID)

            self.db.session.delete(task)
            self.assertEqual(self._get_tasks_count(), 0)

            # create_task.POST
            self.client.post(url_for('task.create_task'), data=dict(
                task_id=None,
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": "<",
                    "price": "105"
                }""",
                user=user.id
            ), follow_redirects=False)

            self.assertEqual(self._get_tasks_count(), 1)

            task = self.db.session.query(Tasks).first()

            # edit_task.POST
            self.client.post(url_for('task.edit_task'), data=dict(
                task_id=task.task_id,
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": "<",
                    "price": "110"
                }""",
                user=user.id
            ), follow_redirects=False)

            task = self.db.session.query(Tasks).first()
            task_params = loads(task.task_params)
            self.assertEqual(int(task_params['price']), 110)
            self.assertEqual(int(task_params['id']), task.task_id)

    def test_admin(self):
        self._create_admin()
        self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)

        with self.app.test_request_context():
            # monitor_tasks.GET
            page = self.client.get(url_for('task.monitor_tasks'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            task = self._create_task()
            self.assertEqual(task.task_status, TaskStatus.ACTIVE)

            # cancel_active_task.GET
            self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
            self.assertEqual(task.task_status, TaskStatus.ACTIVE)

            # edit user telegram_id
            user = self._get_user_by_login(self.ADMIN_LOGIN)
            self._edit_exist_user(user_id=user.id, telegram_id=self.COMMON_TELEGRAM_ID)

            # cancel_active_task.GET
            self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
            self.assertEqual(task.task_status, TaskStatus.CANCELED)

            # get_config_task.GET
            task_config = self.client.get(url_for('task.get_config_task', task_name='alert'), follow_redirects=False)
            self.assertEqual(task_config.status_code, 200)

            self.db.session.delete(task)
            self.assertEqual(self._get_tasks_count(), 0)

            # create_task.POST
            self.client.post(url_for('task.create_task'), data=dict(
                task_id=None,
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": "<",
                    "price": "105"
                }""",
                user=user.id
            ), follow_redirects=False)

            self.assertEqual(self._get_tasks_count(), 1)

            task = self.db.session.query(Tasks).first()

            # edit_task.POST
            self.client.post(url_for('task.edit_task'), data=dict(
                task_id=task.task_id,
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": "<",
                    "price": "110"
                }""",
                user=user.id
            ), follow_redirects=False)

            task = self.db.session.query(Tasks).first()
            task_params = loads(task.task_params)
            self.assertEqual(int(task_params['price']), 110)
            self.assertEqual(int(task_params['id']), task.task_id)

    def test_user(self):
        self._create_user()
        self._login(self.USER_LOGIN, self.USER_PASSWORD)

        with self.app.test_request_context():
            # monitor_tasks.GET
            page = self.client.get(url_for('task.monitor_tasks'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            task = self._create_task()
            self.assertEqual(task.task_status, TaskStatus.ACTIVE)

            # cancel_active_task.GET
            self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
            self.assertEqual(task.task_status, TaskStatus.ACTIVE)

            # edit user telegram_id
            user = self._get_user_by_login(self.USER_LOGIN)
            self._edit_exist_user(user_id=user.id, telegram_id=self.COMMON_TELEGRAM_ID)

            # cancel_active_task.GET
            self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
            self.assertEqual(task.task_status, TaskStatus.CANCELED)

            # get_config_task.GET
            task_config = self.client.get(url_for('task.get_config_task', task_name='alert'), follow_redirects=False)
            self.assertEqual(task_config.status_code, 200)

            self.db.session.delete(task)
            self.assertEqual(self._get_tasks_count(), 0)

            # create_task.POST
            self.client.post(url_for('task.create_task'), data=dict(
                task_id=None,
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": "<",
                    "price": "105"
                }""",
                user=user.id
            ), follow_redirects=False)

            self.assertEqual(self._get_tasks_count(), 1)

            task = self.db.session.query(Tasks).first()

            # edit_task.POST
            self.client.post(url_for('task.edit_task'), data=dict(
                task_id=task.task_id,
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": "<",
                    "price": "110"
                }""",
                user=user.id
            ), follow_redirects=False)

            task = self.db.session.query(Tasks).first()
            task_params = loads(task.task_params)
            self.assertEqual(int(task_params['price']), 110)
            self.assertEqual(int(task_params['id']), task.task_id)

    def test_group(self):
        self._create_group()
        self._login(self.GROUP_LOGIN, self.GROUP_PASSWORD)

        with self.app.test_request_context():
            # monitor_tasks.GET
            page = self.client.get(url_for('task.monitor_tasks'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            task = self._create_task()
            self.assertEqual(task.task_status, TaskStatus.ACTIVE)

            # cancel_active_task.GET
            self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
            self.assertEqual(task.task_status, TaskStatus.ACTIVE)

            # edit user telegram_id
            user = self._get_user_by_login(self.GROUP_LOGIN)
            self._edit_exist_user(user_id=user.id, telegram_id=self.COMMON_TELEGRAM_ID)

            # cancel_active_task.GET
            self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
            self.assertEqual(task.task_status, TaskStatus.CANCELED)

            # get_config_task.GET
            task_config = self.client.get(url_for('task.get_config_task', task_name='alert'), follow_redirects=False)
            self.assertEqual(task_config.status_code, 200)

            self.db.session.delete(task)
            self.assertEqual(self._get_tasks_count(), 0)

            # create_task.POST
            self.client.post(url_for('task.create_task'), data=dict(
                task_id=None,
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": "<",
                    "price": "105"
                }""",
                user=user.id
            ), follow_redirects=False)

            self.assertEqual(self._get_tasks_count(), 1)

            task = self.db.session.query(Tasks).first()

            # edit_task.POST
            self.client.post(url_for('task.edit_task'), data=dict(
                task_id=task.task_id,
                task_name='alert',
                task_params="""{
                    "period": "2m",
                    "duration": "1M",
                    "strategy": "alert",
                    "symbol": "DASHUSDT",
                    "condition": "<",
                    "price": "110"
                }""",
                user=user.id
            ), follow_redirects=False)

            task = self.db.session.query(Tasks).first()
            task_params = loads(task.task_params)
            self.assertEqual(int(task_params['price']), 110)
            self.assertEqual(int(task_params['id']), task.task_id)

    def test_task_cycle(self):
        Task('/task create strategy=alert symbol=BTCUSDT condition=> price=10000', self.COMMON_TELEGRAM_ID, None)

        self.assertEqual(self._get_tasks_count(), 1)

        cnt_notif = self.db.session.query(Notifications).count()
        self.assertEqual(cnt_notif, 1)

        task = self.db.session.query(Tasks).first()
        self.assertEqual(loads(task.task_params)['strategy'], 'alert')
        self.assertEqual(loads(task.task_params)['price'], '10000')
        self.assertEqual(loads(task.task_params)['symbol'], 'BTCUSDT')
        self.assertEqual(loads(task.task_params)['condition'], '>')

        notif = self.db.session.query(Notifications).first()
        self.assertEqual(notif.notif_text, 'Task with id={} created'.format(task.task_id))
        self.db.session.delete(notif)

        Task('/task edit id = {} condition=< price=9000'.format(task.task_id), self.COMMON_TELEGRAM_ID, None)

        self.assertEqual(loads(task.task_params)['price'], '9000')
        self.assertEqual(loads(task.task_params)['condition'], '<')

        notif = self.db.session.query(Notifications).first()
        self.assertEqual(notif.notif_text, 'Task with id={} edited'.format(task.task_id))
        self.db.session.delete(notif)

        Task('/task cancel id = {}'.format(task.task_id), self.COMMON_TELEGRAM_ID, None)
        self.assertEqual(task.task_status, TaskStatus.CANCELED)

        notif = self.db.session.query(Notifications).first()
        self.assertEqual(notif.notif_text, 'Task with id={} canceled'.format(task.task_id))
        self.db.session.delete(notif)

    def test_task_incorrect(self):
        user = self._create_new_user()
        self._login(user.login, self.COMMON_PASSWORD)

        # get_config_task.GET
        task_config = self.client.get(url_for('task.get_config_task', task_name='incorrect_task'),
                                      follow_redirects=False)
        self.assertEqual(task_config.status_code, 200)

        task_config_obj = loads(task_config.data)
        self.assertIsNone(task_config_obj.get('params'))
        self.assertEqual(user.id, task_config_obj.get('user_id'))

    def test_task_alert(self):
        user = self._create_new_user()
        self._login(user.login, self.COMMON_PASSWORD)

        # get_config_task.GET
        task_config = self.client.get(url_for('task.get_config_task', task_name='alert'), follow_redirects=False)
        self.assertEqual(task_config.status_code, 200)

        task_config_obj = loads(task_config.data)
        self.assertIsNotNone(task_config_obj.get('params'))
        self.assertEqual(user.id, task_config_obj.get('user_id'))

        # create_task.POST
        # User without telegram_id
        self.client.post(url_for('task.create_task'), data=dict(
            task_id=None,
            task_name='alert',
            task_params="""{
                "period": "2m",
                "duration": "1M",
                "strategy": "alert",
                "symbol": "DASHUSDT",
                "condition": "<",
                "price": "105"
            }""",
            user=user.id
        ), follow_redirects=False)

        self.assertEqual(self._get_tasks_count(), 0)

        user = self._create_new_user(telegram_id=self.COMMON_TELEGRAM_ID)
        child_user = self._create_new_user(telegram_id=self.COMMON_TELEGRAM_ID)

        self._login(user.login, self.COMMON_PASSWORD)

        # create_task.POST
        # Incorrect permissions (owner_id)
        self.client.post(url_for('task.create_task'), data=dict(
            task_id=None,
            task_name='incorrect_task',
            task_params="""{
                "period": "2m",
                "duration": "1M",
                "strategy": "incorrect_task",
                "symbol": "DASHUSDT",
                "condition": "<",
                "price": "105"
            }""",
            user=child_user.id
        ), follow_redirects=False)

        self.assertEqual(self._get_tasks_count(), 0)

        # create_task.POST
        # Incorrect task_name
        self.client.post(url_for('task.create_task'), data=dict(
            task_id=None,
            task_name='incorrect_task',
            task_params="""{
                "period": "2m",
                "duration": "1M",
                "strategy": "incorrect_task",
                "symbol": "DASHUSDT",
                "condition": "<",
                "price": "105"
            }""",
            user=user.id
        ), follow_redirects=False)

        self.assertEqual(self._get_tasks_count(), 0)

        # create_task.POST
        # Incorrect symbol
        self.client.post(url_for('task.create_task'), data=dict(
            task_id=None,
            task_name='alert',
            task_params="""{
                "period": "2m",
                "duration": "1M",
                "strategy": "alert",
                "symbol": "SHITCOINUSDT",
                "condition": "<",
                "price": "105"
            }""",
            user=user.id
        ), follow_redirects=False)

        self.assertEqual(self._get_tasks_count(), 0)

        # create_task.POST
        # Incorrect condition
        self.client.post(url_for('task.create_task'), data=dict(
            task_id=None,
            task_name='alert',
            task_params="""{
                "period": "2m",
                "duration": "1M",
                "strategy": "alert",
                "symbol": "DASHUSDT",
                "condition": "=<",
                "price": "105"
            }""",
            user=user.id
        ), follow_redirects=False)

        self.assertEqual(self._get_tasks_count(), 0)

        child_user = self._create_new_user(telegram_id=self.COMMON_TELEGRAM_ID, owner_id=user.id)

        # create_task.POST
        self.client.post(url_for('task.create_task'), data=dict(
            task_id=None,
            task_name='alert',
            task_params="""{
                "period": "2m",
                "duration": "1M",
                "strategy": "alert",
                "symbol": "DASHUSDT",
                "condition": "<",
                "price": "105"
            }""",
            user=child_user.id
        ), follow_redirects=False)

        self.assertEqual(self._get_tasks_count(), 1)

        task = self.db.session.query(Tasks).first()

        # edit_task.POST
        self.client.post(url_for('task.edit_task'), data=dict(
            task_id=task.task_id,
            task_name='alert',
            task_params="""{
                "period": "2m",
                "duration": "1M",
                "strategy": "alert",
                "symbol": "DASHUSDT",
                "condition": "<",
                "price": "110"
            }""",
            user=user.id
        ), follow_redirects=False)

        task = self.db.session.query(Tasks).first()
        task_params = loads(task.task_params)
        self.assertEqual(int(task_params['price']), 110)
        self.assertEqual(int(task_params['id']), task.task_id)

    def test_task_price(self):
        user = self._create_new_user()
        self._login(user.login, self.COMMON_PASSWORD)

        # get_config_task.GET
        task_config = self.client.get(url_for('task.get_config_task', task_name='price'), follow_redirects=False)
        self.assertEqual(task_config.status_code, 200)

        task_config_obj = loads(task_config.data)
        self.assertIsNotNone(task_config_obj.get('params'))
        self.assertEqual(user.id, task_config_obj.get('user_id'))

    def test_task_envelope(self):
        user = self._create_new_user()
        self._login(user.login, self.COMMON_PASSWORD)

        # get_config_task.GET
        task_config = self.client.get(url_for('task.get_config_task', task_name='envelope'), follow_redirects=False)
        self.assertEqual(task_config.status_code, 200)

        task_config_obj = loads(task_config.data)
        self.assertIsNotNone(task_config_obj.get('params'))
        self.assertEqual(user.id, task_config_obj.get('user_id'))

    def test_task_volume(self):
        user = self._create_new_user()
        self._login(user.login, self.COMMON_PASSWORD)

        # get_config_task.GET
        task_config = self.client.get(url_for('task.get_config_task', task_name='volume'), follow_redirects=False)
        self.assertEqual(task_config.status_code, 200)

        task_config_obj = loads(task_config.data)
        self.assertIsNotNone(task_config_obj.get('params'))
        self.assertEqual(user.id, task_config_obj.get('user_id'))

    def test_task_dump_price_history(self):
        user = self._create_new_user()
        self._login(user.login, self.COMMON_PASSWORD)

        # get_config_task.GET
        task_config = self.client.get(url_for('task.get_config_task', task_name='dump_price_history'),
                                      follow_redirects=False)
        self.assertEqual(task_config.status_code, 200)

        task_config_obj = loads(task_config.data)
        self.assertIsNotNone(task_config_obj.get('params'))
        self.assertEqual(user.id, task_config_obj.get('user_id'))
