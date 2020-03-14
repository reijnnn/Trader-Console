from tests.base_test_case import BaseTestCase
from flask                import url_for

class TestFrontendBP(BaseTestCase):
	@classmethod
	def setUpClass(self):
		self._init_app(self)
		self._init_db(self)
		self._print_test_desc(self, __name__)

	def setUp(self):
		self._logout()

	def tearDown(self):
		pass

	def test_access(self):
		with self.app.test_request_context():
			# index.GET
			page = self.client.get(url_for('frontend.index'), follow_redirects=False)
			self.assertEqual(page.status_code, 302)

			# logs.GET
			page = self.client.get(url_for('frontend.logs'), follow_redirects=False)
			self.assertEqual(page.status_code, 302)

	def test_super_admin(self):
		self._create_super_admin()
		self._login(self.SUPER_ADMIN_LOGIN, self.SUPER_ADMIN_PASSWORD)

		with self.app.test_request_context():
			# index.GET
			page = self.client.get(url_for('frontend.index'), follow_redirects=False)
			self.assertEqual(page.status_code, 200)

			# logs.GET
			page = self.client.get(url_for('frontend.logs'), follow_redirects=False)
			self.assertEqual(page.status_code, 200)

	def test_admin(self):
		self._create_admin()
		self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)

		with self.app.test_request_context():
			# index.GET
			page = self.client.get(url_for('frontend.index'), follow_redirects=False)
			self.assertEqual(page.status_code, 200)

			# logs.GET
			page = self.client.get(url_for('frontend.logs'), follow_redirects=False)
			self.assertEqual(page.status_code, 302)

	def test_user(self):
		self._create_user()
		self._login(self.USER_LOGIN, self.USER_PASSWORD)

		with self.app.test_request_context():
			# index.GET
			page = self.client.get(url_for('frontend.index'), follow_redirects=False)
			self.assertEqual(page.status_code, 200)

			# logs.GET
			page = self.client.get(url_for('frontend.logs'), follow_redirects=False)
			self.assertEqual(page.status_code, 302)

	def test_group_access(self):
		self._create_group()
		self._login(self.GROUP_LOGIN, self.GROUP_PASSWORD)

		with self.app.test_request_context():
			# index.GET
			page = self.client.get(url_for('frontend.index'), follow_redirects=False)
			self.assertEqual(page.status_code, 200)

			# logs.GET
			page = self.client.get(url_for('frontend.logs'), follow_redirects=False)
			self.assertEqual(page.status_code, 302)

	def test_inactive_user(self):
		self._create_inactive_user()
		self._login(self.INACTIVE_USER_LOGIN, self.INACTIVE_USER_PASSWORD)
		self.test_access()

	def test_reset_user(self):
		self._create_reset_user()
		self._login(self.RESET_USER_LOGIN, self.RESET_USER_PASSWORD)
		self.test_access()
