from tests.base_test_case import BaseTestCase
from flask import url_for
from trader.user.models import UserRole, UserStatus


class TestUserBP(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls._init_app(cls)
        cls._init_db(cls)
        cls._print_test_desc(cls, __name__)

    def setUp(self):
        self._logout()

    def tearDown(self):
        pass

    def test_access(self):
        with self.app.test_request_context():
            # login.GET
            page = self.client.get(url_for('user.login'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            # users_list.GET
            page = self.client.get(url_for('user.users_list'), follow_redirects=False)
            self.assertEqual(page.status_code, 302)

            # create_user.GET
            page = self.client.get(url_for('user.create_user'), follow_redirects=False)
            self.assertEqual(page.status_code, 302)

            # edit_user.GET
            user_login = self._generate_login()
            user = self._create_new_user(login=user_login)

            page = self.client.get(url_for('user.edit_user', user_id=user.id), follow_redirects=False)
            self.assertEqual(page.status_code, 302)

            # delete_user.GET
            self.client.get(url_for('user.delete_user', user_id=user.id))
            user = self._get_user_by_login(user_login)
            self.assertIsNotNone(user)

    def test_super_admin(self):
        self._create_super_admin()

        with self.app.test_request_context():
            self._login(self.SUPER_ADMIN_LOGIN, self.SUPER_ADMIN_PASSWORD)

            # users_list.GET
            page = self.client.get(url_for('user.users_list'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            # create_user.GET
            page = self.client.get(url_for('user.create_user'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            # create_user.POST | user with role "SUPER_ADMIN"
            new_super_admin_login = self._generate_login()
            self.client.post(url_for('user.create_user'), data=dict(
                login=new_super_admin_login,
                password=self.COMMON_PASSWORD,
                role=UserRole.SUPER_ADMIN,
                chat_id=None,
                status=UserStatus.ACTIVE
            ), follow_redirects=True)

            user = self._get_user_by_login(new_super_admin_login)
            self.assertIsNone(user)

            # create_user.POST | user with role "ADMIN"
            new_admin_login = self._generate_login()
            self.client.post(url_for('user.create_user'), data=dict(
                login=new_admin_login,
                password=self.COMMON_PASSWORD,
                role=UserRole.ADMIN,
                chat_id=None,
                status=UserStatus.INACTIVE
            ), follow_redirects=True)

            user = self._get_user_by_login(new_admin_login)
            self.assertIsNotNone(user)

            # edit_user.GET
            page = self.client.get(url_for('user.edit_user', user_id=user.id), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            # delete_user.GET
            self.client.get(url_for('user.delete_user', user_id=user.id))
            user = self._get_user_by_login(new_admin_login)
            self.assertIsNone(user)

            # create_user.POST | user with role "USER"
            new_user_login = self._generate_login()
            self.client.post(url_for('user.create_user'), data=dict(
                login=new_user_login,
                password=self.COMMON_PASSWORD,
                role=UserRole.USER,
                chat_id=None,
                status=UserStatus.ACTIVE
            ), follow_redirects=True)

            user = self._get_user_by_login(new_user_login)
            self.assertIsNotNone(user)

            # delete_user.GET
            self.client.get(url_for('user.delete_user', user_id=user.id))
            user = self._get_user_by_login(new_user_login)
            self.assertIsNone(user)

            # create_user.POST | user with role "GROUP"
            new_group_login = self._generate_login()
            self.client.post(url_for('user.create_user'), data=dict(
                login=new_group_login,
                password=self.COMMON_PASSWORD,
                role=UserRole.GROUP,
                chat_id=None,
                status=UserStatus.ACTIVE
            ), follow_redirects=True)

            user = self._get_user_by_login(new_group_login)
            self.assertIsNotNone(user)

            # delete_user.GET
            self.client.get(url_for('user.delete_user', user_id=user.id))
            user = self._get_user_by_login(new_group_login)
            self.assertIsNone(user)

    def test_admin(self):
        self._create_admin()

        with self.app.test_request_context():
            self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)

            # users_list.GET
            page = self.client.get(url_for('user.users_list'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            # create_user.GET
            page = self.client.get(url_for('user.create_user'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            # create_user.POST | user with role "ADMIN"
            new_admin_login = self._generate_login()
            self.client.post(url_for('user.create_user'), data=dict(
                login=new_admin_login,
                password=self.COMMON_PASSWORD,
                role=UserRole.ADMIN,
                chat_id=None,
                status=UserStatus.INACTIVE
            ), follow_redirects=True)

            user = self._get_user_by_login(new_admin_login)
            self.assertIsNotNone(user)

            # edit_user.GET
            page = self.client.get(url_for('user.edit_user', user_id=user.id), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            # delete_user.GET
            self.client.get(url_for('user.delete_user', user_id=user.id))
            user = self._get_user_by_login(new_admin_login)
            self.assertIsNone(user)

            # create_user.POST | user with role "USER"
            new_user_login = self._generate_login()
            self.client.post(url_for('user.create_user'), data=dict(
                login=new_user_login,
                password=self.COMMON_PASSWORD,
                role=UserRole.ADMIN,
                chat_id=None,
                status=UserStatus.INACTIVE
            ), follow_redirects=True)

            user = self._get_user_by_login(new_user_login)
            self.assertIsNotNone(user)

            # edit_user.GET
            page = self.client.get(url_for('user.edit_user', user_id=user.id), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            # edit_user.POST
            edit_role = UserRole.USER
            edit_status = UserStatus.ACTIVE
            edit_chat_id = -99
            edit_password = 'EDIT_PASSWORD'

            self.client.post(url_for('user.edit_user', user_id=user.id), data=dict(
                login=new_user_login,
                password=edit_password,
                role=edit_role,
                chat_id=edit_chat_id,
                status=edit_status,
                user_id=user.id
            ), follow_redirects=True)

            user = self._get_user_by_login(new_user_login)
            self.assertIsNotNone(user)
            self.assertEqual(edit_role, user.role)
            self.assertEqual(edit_status, user.status)
            self.assertEqual(edit_chat_id, user.telegram_id)

            # check new password
            self._login(new_user_login, edit_password)

            page = self.client.get(url_for('frontend.index'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)

            # reset_password_user.GET
            self.client.get(url_for('user.reset_password_user', user_id=user.id), follow_redirects=False)

            user = self._get_user_by_login(new_user_login)
            self.assertEqual(user.status, UserStatus.RESET)
            self.assertIsNotNone(user.reset_code)

            self._logout()

            # change_password_user.GET
            page = self.client.get(url_for('user.change_password_user', user_id=user.id, reset_code=user.reset_code),
                                   follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            # change_password_user.POST
            new_password = 'NEW_PASSWORD1'
            self.client.post(url_for('user.change_password_user', user_id=user.id, reset_code=user.reset_code),
                             data=dict(
                                        login=new_user_login,
                                        password=new_password,
                                        confirm=new_password
                                    ), follow_redirects=True)

            # check new password
            self._login(new_user_login, new_password)

            page = self.client.get(url_for('frontend.index'), follow_redirects=False)
            self.assertEqual(page.status_code, 200)

            self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)

            # delete_user.GET
            self.client.get(url_for('user.delete_user', user_id=user.id))
            user = self._get_user_by_login(new_user_login)
            self.assertIsNone(user)

    def test_user(self):
        self._create_user()

        with self.app.test_request_context():
            self._login(self.USER_LOGIN, self.USER_PASSWORD)

            # users_list.GET
            page = self.client.get(url_for('user.users_list'), follow_redirects=False)
            self.assertEqual(page.status_code, 302)

            # create_user.GET
            page = self.client.get(url_for('user.create_user'), follow_redirects=False)
            self.assertEqual(page.status_code, 302)

            # create_user.POST | user with role "USER"
            new_user_login = self._generate_login()
            self.client.post(url_for('user.create_user'), data=dict(
                login=new_user_login,
                password=self.COMMON_PASSWORD,
                role=UserRole.USER,
                chat_id=None,
                status=UserStatus.ACTIVE
            ), follow_redirects=True)

            user = self._get_user_by_login(new_user_login)
            self.assertIsNone(user)

    def test_group(self):
        self._create_group()

        with self.app.test_request_context():
            self._login(self.GROUP_LOGIN, self.GROUP_PASSWORD)

            # users_list.GET
            page = self.client.get(url_for('user.users_list'), follow_redirects=False)
            self.assertEqual(page.status_code, 302)

            # create_user.GET
            page = self.client.get(url_for('user.create_user'), follow_redirects=False)
            self.assertEqual(page.status_code, 302)

            # create_user.POST | user with role "GROUP"
            new_group_login = self._generate_login()
            self.client.post(url_for('user.create_user'), data=dict(
                login=new_group_login,
                password=self.COMMON_PASSWORD,
                role=UserRole.GROUP,
                chat_id=None,
                status=UserStatus.ACTIVE
            ), follow_redirects=True)

            user = self._get_user_by_login(new_group_login)
            self.assertIsNone(user)
