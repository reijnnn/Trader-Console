import unittest

from flask                   import url_for, current_app
from trader.user.models      import Users, User_role, User_status
from trader.task.models      import Tasks, Task_status
from trader.proxy_bot.models import Proxies

from string import ascii_letters
from random import choice

class BaseTestCase(unittest.TestCase):

	def _init_app(self):
		self.COMMON_PASSWORD    = '12345'
		self.COMMON_TELEGRAM_ID = -123454321

		self.app    = current_app
		self.client = self.app.test_client()

	def _print_test_desc(self, test_name):
		self.app.logger.info("\n\n\nStart " + test_name + "\n")

	def _init_db(self):
		from trader.extensions import db
		self.db = db

		db.drop_all()
		db.create_all()

	def _create_new_user(self, login=None, password=None, role=None, status=None, telegram_id=None, owner_id=None):
		if login is None:
			login = self._generate_login()
		if password is None:
			password = self.COMMON_PASSWORD
		if role is None:
			role = User_role.USER
		if status is None:
			status = User_status.ACTIVE

		user = Users()
		user.login       = login
		user.role        = role
		user.status      = status
		user.owner_id    = owner_id
		user.telegram_id = telegram_id
		user.set_password(password)

		self.db.session.add(user)
		self.db.session.commit()

		return user

	def _edit_exist_user(self, user_id, password=None, role=None, status=None, telegram_id=None, owner_id=None):
		user = self.db.session.query(Users).filter_by(id=user_id).first()

		if password:
			user.set_password(password)
		if role:
			user.role = role
		if status:
			user.status = status
		if owner_id:
			user.owner_id = owner_id
		if telegram_id:
			user.telegram_id = telegram_id

		self.db.session.commit()

		return user

	def _create_super_admin(self):
		self.SUPER_ADMIN_LOGIN    = 'super_admin'
		self.SUPER_ADMIN_PASSWORD = 'super_admin'

		return self._create_new_user(
			login=self.SUPER_ADMIN_LOGIN,
			password=self.SUPER_ADMIN_PASSWORD,
			role=User_role.SUPER_ADMIN,
			status=User_status.ACTIVE
		)

	def _create_admin(self):
		self.ADMIN_LOGIN    = 'admin'
		self.ADMIN_PASSWORD = 'admin'

		return self._create_new_user(
			login=self.ADMIN_LOGIN,
			password=self.ADMIN_PASSWORD,
			role=User_role.ADMIN,
			status=User_status.ACTIVE
		)

	def _create_user(self):
		self.USER_LOGIN    = 'user'
		self.USER_PASSWORD = 'user'

		return self._create_new_user(
			login=self.USER_LOGIN,
			password=self.USER_PASSWORD,
			role=User_role.USER,
			status=User_status.ACTIVE
		)

	def _create_group(self):
		self.GROUP_LOGIN    = 'group'
		self.GROUP_PASSWORD = 'group'

		return self._create_new_user(
			login=self.GROUP_LOGIN,
			password=self.GROUP_PASSWORD,
			role=User_role.GROUP,
			status=User_status.ACTIVE
		)

	def _create_inactive_user(self):
		self.INACTIVE_USER_LOGIN    = 'inactive_user'
		self.INACTIVE_USER_PASSWORD = 'inactive_user'

		return self._create_new_user(
			login=self.INACTIVE_USER_LOGIN,
			password=self.INACTIVE_USER_PASSWORD,
			role=User_role.USER,
			status=User_status.INACTIVE
		)

	def _create_reset_user(self):
		self.RESET_USER_LOGIN     = 'reset_user'
		self.RESET_USER_PASSWORD  = 'reset_user'

		return self._create_new_user(
			login=self.RESET_USER_LOGIN,
			password=self.RESET_USER_PASSWORD,
			role=User_role.USER,
			status=User_status.RESET
		)

	def _get_user_by_login(self, login):
		return self.db.session.query(Users).filter_by(login=login).first()

	def _generate_login(self):
		return ''.join([choice(ascii_letters) for n in range(10)]).lower()

	def _login(self, login, password):
		with self.app.test_request_context():
			return self.client.post(url_for('user.login'), data=dict(
					login=login,
					password=password
			), follow_redirects=False)

	def _logout(self):
		with self.app.test_request_context():
			return self.client.get(url_for('user.logout'), follow_redirects=False)

	def _create_task(self):
		task = Tasks(
			task_name           = 'price',
			task_params         = '{"symbol": "BTCUSDT", "strategy": "price"}',
			task_status         = Task_status.ACTIVE,
			chat_id             = self.COMMON_TELEGRAM_ID,
			reply_to_message_id = None
		)
		self.db.session.add(task)
		self.db.session.commit()

		return task

	def _create_proxy(self):
		proxy = Proxies (
			proxy_type    = 'https',
			proxy_ip      = '127.0.0.1',
			proxy_port    = '9090'
		)
		self.db.session.add(proxy)
		self.db.session.commit()

		return proxy
