from flask import url_for

from tests.base_test_case import BaseTestCase
from trader.extensions import proxy_bot
from trader.proxy_bot.models import Proxies


class TestProxyBP(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls._init_app()
        cls._init_db()
        cls._print_test_desc(__name__)

    def setUp(self):
        self._logout()
        self.db.session.query(Proxies).delete()

    def tearDown(self):
        pass

    def common_error_access(self):
        with self.app.test_request_context():
            # monitor_proxy_bot.GET
            page = self.client.get(url_for('proxy_bot.monitor_proxy_bot'), follow_redirects=False)
            self.assertEqual(page.status_code, 302)

            self.assertEqual(proxy_bot.get_status(), 'inactive')

            # start_proxy_bot.GET
            self.client.get(url_for('proxy_bot.start_proxy_bot'), follow_redirects=False)
            self.assertNotEqual(proxy_bot.get_status(), 'active')

            proxy_bot.restart()

            # stop_proxy_bot.GET
            self.client.get(url_for('proxy_bot.stop_proxy_bot'), follow_redirects=False)
            self.assertNotEqual(proxy_bot.get_status(), 'inactive')

            proxy_bot.cancel()

            cnt_proxy = self._get_proxies_count()

            # add_proxy.POST
            self.client.post(url_for('proxy_bot.add_proxy'), data=dict(
                proxy_list='https:127.0.0.1:8081;https:127.0.0.1:8082',
            ), follow_redirects=False)

            cnt_proxy_upd = self._get_proxies_count()
            self.assertEqual(cnt_proxy, cnt_proxy_upd)

            proxy = self._create_proxy()
            cnt_proxy = self._get_proxies_count()

            # delete_proxy.GET
            self.client.get(url_for('proxy_bot.delete_proxy', proxy_id=proxy.proxy_id), follow_redirects=False)

            cnt_proxy_upd = self._get_proxies_count()
            self.assertEqual(cnt_proxy, cnt_proxy_upd)

    def test_access(self):
        self.common_error_access()

    def test_super_admin(self):
        self._create_super_admin()
        self._login(self.SUPER_ADMIN_LOGIN, self.SUPER_ADMIN_PASSWORD)

        with self.app.test_request_context():
            # monitor_proxy_bot.GET
            page = self.client.get(url_for('proxy_bot.monitor_proxy_bot'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            self.assertEqual(proxy_bot.get_status(), 'inactive')

            # start_proxy_bot.GET
            self.client.get(url_for('proxy_bot.start_proxy_bot'), follow_redirects=False)
            self.assertEqual(proxy_bot.get_status(), 'active')

            # stop_proxy_bot.GET
            self.client.get(url_for('proxy_bot.stop_proxy_bot'), follow_redirects=False)
            self.assertEqual(proxy_bot.get_status(), 'inactive')

            cnt_proxy = self._get_proxies_count()

            # add_proxy.POST
            self.client.post(url_for('proxy_bot.add_proxy'), data=dict(
                proxy_list='https:127.0.0.1:8081;https:127.0.0.1:8082',
            ), follow_redirects=False)

            # add_proxy.POST
            self.client.post(url_for('proxy_bot.add_proxy'), data=dict(
                proxy_list='https:127.0.0.1:8081;sock:127.0.0.1',
            ), follow_redirects=False)

            cnt_proxy_upd = self._get_proxies_count()
            self.assertEqual(cnt_proxy_upd - cnt_proxy, 2)

            proxy = self._create_proxy()
            cnt_proxy = self._get_proxies_count()

            # delete_proxy.GET
            self.client.get(url_for('proxy_bot.delete_proxy', proxy_id=proxy.proxy_id), follow_redirects=False)

            cnt_proxy_upd = self._get_proxies_count()
            self.assertEqual(cnt_proxy - cnt_proxy_upd, 1)

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
