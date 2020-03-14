from tests.base_test_case import BaseTestCase
from flask                import url_for

class TestSQLBP(BaseTestCase):
	@classmethod
	def setUpClass(self):
		self._init_app(self)
		self._init_db(self)
		self._print_test_desc(self, __name__)

	def setUp(self):
		self._logout()

	def tearDown(self):
		pass

	def common_error_access(self):
		with self.app.test_request_context():
			# execute_sql.GET
			page = self.client.get(url_for('sql.execute_sql'), follow_redirects=False)
			self.assertEqual(page.status_code, 302)

	def test_access(self):
		self.common_error_access()

	def test_super_admin(self):
		self._create_super_admin()
		self._login(self.SUPER_ADMIN_LOGIN, self.SUPER_ADMIN_PASSWORD)

		with self.app.test_request_context():
			# execute_sql.GET
			page = self.client.get(url_for('sql.execute_sql'), follow_redirects=False)
			self.assertEqual(page.status_code, 200)

	def test_admin(self):
		self._create_admin()
		self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)
		self.common_error_access()

	def test_user(self):
		self._create_user()
		self._login(self.USER_LOGIN, self.USER_PASSWORD)
		self.common_error_access()

	def test_group(self):
		self._create_group()
		self._login(self.GROUP_LOGIN, self.GROUP_PASSWORD)
		self.common_error_access()
