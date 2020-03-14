from tests.base_test_case import BaseTestCase
from flask                import url_for
from trader.task.models   import Tasks, Task_status
from trader.task.task     import Task
from trader.telegram_bot.models import Notifications
from json                 import loads

class TestTaskBP(BaseTestCase):
	@classmethod
	def setUpClass(self):
		self._init_app(self)
		self._init_db(self)
		self._print_test_desc(self, __name__)

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
			self.assertEqual(task.task_status, Task_status.ACTIVE)

			# cancel_active_task.GET
			page = self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
			self.assertNotEqual(task.task_status, Task_status.CANCELED)

	def test_super_admin(self):
		self._create_super_admin()
		self._login(self.SUPER_ADMIN_LOGIN, self.SUPER_ADMIN_PASSWORD)

		with self.app.test_request_context():
			# monitor_tasks.GET
			page = self.client.get(url_for('task.monitor_tasks'), follow_redirects=False)
			self.assertEqual(page.status_code, 200)

			task = self._create_task()
			self.assertEqual(task.task_status, Task_status.ACTIVE)

			# cancel_active_task.GET
			page = self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
			self.assertEqual(task.task_status, Task_status.CANCELED)

	def test_admin(self):
		self._create_admin()
		self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)

		with self.app.test_request_context():
			# monitor_tasks.GET
			page = self.client.get(url_for('task.monitor_tasks'), follow_redirects=False)
			self.assertEqual(page.status_code, 200)

			task = self._create_task()
			self.assertEqual(task.task_status, Task_status.ACTIVE)

			# cancel_active_task.GET
			page = self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
			self.assertEqual(task.task_status, Task_status.ACTIVE)

			# edit user teleram_id
			user = self._get_user_by_login(self.ADMIN_LOGIN)
			user = self._edit_exist_user(user.id, telegram_id=self.COMMON_TELEGRAM_ID)

			# cancel_active_task.GET
			page = self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
			self.assertEqual(task.task_status, Task_status.CANCELED)

	def test_user(self):
		self._create_user()
		self._login(self.USER_LOGIN, self.USER_PASSWORD)

		with self.app.test_request_context():
			# monitor_tasks.GET
			page = self.client.get(url_for('task.monitor_tasks'), follow_redirects=False)
			self.assertEqual(page.status_code, 200)

			task = self._create_task()
			self.assertEqual(task.task_status, Task_status.ACTIVE)

			# cancel_active_task.GET
			page = self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
			self.assertEqual(task.task_status, Task_status.ACTIVE)

			# edit user teleram_id
			user = self._get_user_by_login(self.USER_LOGIN)
			user = self._edit_exist_user(user.id, telegram_id=self.COMMON_TELEGRAM_ID)

			# cancel_active_task.GET
			page = self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
			self.assertEqual(task.task_status, Task_status.CANCELED)

	def test_group(self):
		self._create_group()
		self._login(self.GROUP_LOGIN, self.GROUP_PASSWORD)

		with self.app.test_request_context():
			# monitor_tasks.GET
			page = self.client.get(url_for('task.monitor_tasks'), follow_redirects=False)
			self.assertEqual(page.status_code, 200)

			task = self._create_task()
			self.assertEqual(task.task_status, Task_status.ACTIVE)

			# cancel_active_task.GET
			page = self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
			self.assertEqual(task.task_status, Task_status.ACTIVE)

			# edit user teleram_id
			user = self._get_user_by_login(self.GROUP_LOGIN)
			user = self._edit_exist_user(user.id, telegram_id=self.COMMON_TELEGRAM_ID)

			# cancel_active_task.GET
			page = self.client.get(url_for('task.cancel_active_task', task_id=task.task_id), follow_redirects=False)
			self.assertEqual(task.task_status, Task_status.CANCELED)

	def test_task_cycle(self):
		task_cmd  = Task('/task create strategy=alert symbol=BTCUSDT condition=> price=10000', self.COMMON_TELEGRAM_ID, None)
		cnt_tasks = self.db.session.query(Tasks).count()
		self.assertEqual(cnt_tasks, 1)

		cnt_notif = self.db.session.query(Notifications).count()
		self.assertEqual(cnt_notif, 1)

		task  = self.db.session.query(Tasks).first()
		self.assertEqual(loads(task.task_params)['strategy'],  'alert')
		self.assertEqual(loads(task.task_params)['price'],     '10000')
		self.assertEqual(loads(task.task_params)['symbol'],    'BTCUSDT')
		self.assertEqual(loads(task.task_params)['condition'], '>')

		notif = self.db.session.query(Notifications).first()
		self.assertEqual(notif.notif_text, 'Task with id={} created'.format(task.task_id))
		self.db.session.delete(notif)

		task_cmd = Task('/task edit id = {} condition=< price=9000'.format(task.task_id), self.COMMON_TELEGRAM_ID, None)

		self.assertEqual(loads(task.task_params)['price'],     '9000')
		self.assertEqual(loads(task.task_params)['condition'], '<')

		notif = self.db.session.query(Notifications).first()
		self.assertEqual(notif.notif_text, 'Task with id={} edited'.format(task.task_id))
		self.db.session.delete(notif)

		task_cmd = Task('/task cancel id = {}'.format(task.task_id), self.COMMON_TELEGRAM_ID, None)
		self.assertEqual(task.task_status, Task_status.CANCELED)

		notif = self.db.session.query(Notifications).first()
		self.assertEqual(notif.notif_text, 'Task with id={} canceled'.format(task.task_id))
		self.db.session.delete(notif)
