from tests.base_test_case import BaseTestCase
from flask import url_for
from trader.extensions import trader_bot


class TestTraderBP(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls._init_app(cls)
        cls._init_db(cls)
        cls._print_test_desc(cls, __name__)

    def setUp(self):
        self._logout()

    def tearDown(self):
        pass

    def common_error_access(self):
        with self.app.test_request_context():
            # monitor_trader_bot.GET
            page = self.client.get(url_for('trader_bot.monitor_trader_bot'), follow_redirects=False)
            self.assertEqual(page.status_code, 302)

            self.assertEqual(trader_bot.get_status(), 'inactive')

            # start_trader_bot.GET
            self.client.get(url_for('trader_bot.start_trader_bot'), follow_redirects=False)
            self.assertNotEqual(trader_bot.get_status(), 'active')

            trader_bot.restart()

            # stop_trader_bot.GET
            self.client.get(url_for('trader_bot.stop_trader_bot'), follow_redirects=False)
            self.assertNotEqual(trader_bot.get_status(), 'inactive')

            trader_bot.cancel()

    def test_access(self):
        self.common_error_access()

    def test_super_admin(self):
        self._create_super_admin()
        self._login(self.SUPER_ADMIN_LOGIN, self.SUPER_ADMIN_PASSWORD)

        with self.app.test_request_context():
            # monitor_trader_bot.GET
            page = self.client.get(url_for('trader_bot.monitor_trader_bot'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            self.assertEqual(trader_bot.get_status(), 'inactive')

            # start_trader_bot.GET
            self.client.get(url_for('trader_bot.start_trader_bot'), follow_redirects=False)
            self.assertEqual(trader_bot.get_status(), 'active')

            # stop_trader_bot.GET
            self.client.get(url_for('trader_bot.stop_trader_bot'), follow_redirects=False)
            self.assertEqual(trader_bot.get_status(), 'inactive')

    def test_admin(self):
        self._create_admin()
        self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)

        with self.app.test_request_context():
            # monitor_trader_bot.GET
            page = self.client.get(url_for('trader_bot.monitor_trader_bot'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            self.assertEqual(trader_bot.get_status(), 'inactive')

            # start_trader_bot.GET
            self.client.get(url_for('trader_bot.start_trader_bot'), follow_redirects=False)
            self.assertNotEqual(trader_bot.get_status(), 'active')

            trader_bot.restart()

            # stop_trader_bot.GET
            self.client.get(url_for('trader_bot.stop_trader_bot'), follow_redirects=False)
            self.assertNotEqual(trader_bot.get_status(), 'inactive')

            trader_bot.cancel()

    def test_user(self):
        self._create_user()
        self._login(self.USER_LOGIN, self.USER_PASSWORD)
        self.common_error_access()

    def test_group(self):
        self._create_group()
        self._login(self.GROUP_LOGIN, self.GROUP_PASSWORD)
        self.common_error_access()
