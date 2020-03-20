from tests.base_test_case import BaseTestCase
from flask                import url_for
from trader.extensions    import telegram_bot

class TestTelegramBP(BaseTestCase):
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
         self.assertEqual(telegram_bot.get_status(), 'active')

         # stop_telegram_bot.GET
         page = self.client.get(url_for('telegram_bot.stop_telegram_bot'), follow_redirects=False)
         self.assertNotEqual(telegram_bot.get_status(), 'inactive')

         # start_telegram_bot.GET
         page = self.client.get(url_for('telegram_bot.start_telegram_bot'), follow_redirects=False)
         self.assertEqual(telegram_bot.get_status(), 'active')

   def test_access(self):
      self.common_error_access()

      with self.app.test_request_context():
         # monitor_telegram_bot.GET
         page = self.client.get(url_for('telegram_bot.monitor_telegram_bot'), follow_redirects=False)
         self.assertEqual(page.status_code, 302)

   def test_super_admin(self):
      self._create_super_admin()
      self._login(self.SUPER_ADMIN_LOGIN, self.SUPER_ADMIN_PASSWORD)

      with self.app.test_request_context():
         # monitor_telegram_bot.GET
         page = self.client.get(url_for('telegram_bot.monitor_telegram_bot'), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         self.assertEqual(telegram_bot.get_status(), 'active')

         # stop_telegram_bot.GET
         page = self.client.get(url_for('telegram_bot.stop_telegram_bot'), follow_redirects=False)
         self.assertEqual(telegram_bot.get_status(), 'inactive')

         # start_telegram_bot.GET
         page = self.client.get(url_for('telegram_bot.start_telegram_bot'), follow_redirects=False)
         self.assertEqual(telegram_bot.get_status(), 'active')

   def test_admin(self):
      self._create_admin()
      self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)
      self.common_error_access()

      with self.app.test_request_context():
         # monitor_telegram_bot.GET
         page = self.client.get(url_for('telegram_bot.monitor_telegram_bot'), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

   def test_user(self):
      self._create_user()
      self._login(self.USER_LOGIN, self.USER_PASSWORD)
      self.common_error_access()

      with self.app.test_request_context():
         # monitor_telegram_bot.GET
         page = self.client.get(url_for('telegram_bot.monitor_telegram_bot'), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

   def test_group(self):
      self._create_group()
      self._login(self.GROUP_LOGIN, self.GROUP_PASSWORD)
      self.common_error_access()

      with self.app.test_request_context():
         # monitor_telegram_bot.GET
         page = self.client.get(url_for('telegram_bot.monitor_telegram_bot'), follow_redirects=False)
         self.assertEqual(page.status_code, 200)
