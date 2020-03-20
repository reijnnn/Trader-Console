from tests.base_test_case import BaseTestCase
from flask                import url_for
from trader.user.models   import Users, User_role, User_status

class TestUserBP(BaseTestCase):
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
         USER_LOGIN = self._generate_login()
         user = self._create_new_user(login=USER_LOGIN)

         page = self.client.get(url_for('user.edit_user', user_id=user.id), follow_redirects=False)
         self.assertEqual(page.status_code, 302)

         # delete_user.GET
         self.client.get(url_for('user.delete_user', user_id=user.id))
         user = self._get_user_by_login(USER_LOGIN)
         self.assertIsNotNone(user)

   def test_super_admin(self):
      self._create_super_admin()

      with self.app.test_request_context():
         page = self._login(self.SUPER_ADMIN_LOGIN, self.SUPER_ADMIN_PASSWORD)

         # users_list.GET
         page = self.client.get(url_for('user.users_list'), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         # create_user.GET
         page = self.client.get(url_for('user.create_user'), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         # create_user.POST | user with role "SUPER_ADMIN"
         NEW_SUPER_ADMIN_LOGIN = self._generate_login()
         page = self.client.post(url_for('user.create_user'), data=dict(
               login=NEW_SUPER_ADMIN_LOGIN,
               password=self.COMMON_PASSWORD,
               role=User_role.SUPER_ADMIN,
               chat_id=None,
               status=User_status.ACTIVE
         ), follow_redirects=True)

         user = self._get_user_by_login(NEW_SUPER_ADMIN_LOGIN)
         self.assertIsNone(user)

         # create_user.POST | user with role "ADMIN"
         NEW_ADMIN_LOGIN = self._generate_login()
         page = self.client.post(url_for('user.create_user'), data=dict(
               login=NEW_ADMIN_LOGIN,
               password=self.COMMON_PASSWORD,
               role=User_role.ADMIN,
               chat_id=None,
               status=User_status.INACTIVE
         ), follow_redirects=True)

         user = self._get_user_by_login(NEW_ADMIN_LOGIN)
         self.assertIsNotNone(user)

         # edit_user.GET
         page = self.client.get(url_for('user.edit_user', user_id=user.id), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         # delete_user.GET
         self.client.get(url_for('user.delete_user', user_id=user.id))
         user = self._get_user_by_login(NEW_ADMIN_LOGIN)
         self.assertIsNone(user)

         # create_user.POST | user with role "USER"
         NEW_USER_LOGIN = self._generate_login()
         page = self.client.post(url_for('user.create_user'), data=dict(
               login=NEW_USER_LOGIN,
               password=self.COMMON_PASSWORD,
               role=User_role.USER,
               chat_id=None,
               status=User_status.ACTIVE
         ), follow_redirects=True)

         user = self._get_user_by_login(NEW_USER_LOGIN)
         self.assertIsNotNone(user)

         # delete_user.GET
         self.client.get(url_for('user.delete_user', user_id=user.id))
         user = self._get_user_by_login(NEW_USER_LOGIN)
         self.assertIsNone(user)

         # create_user.POST | user with role "GROUP"
         NEW_GROUP_LOGIN = self._generate_login()
         page = self.client.post(url_for('user.create_user'), data=dict(
               login=NEW_GROUP_LOGIN,
               password=self.COMMON_PASSWORD,
               role=User_role.GROUP,
               chat_id=None,
               status=User_status.ACTIVE
         ), follow_redirects=True)

         user = self._get_user_by_login(NEW_GROUP_LOGIN)
         self.assertIsNotNone(user)

         # delete_user.GET
         self.client.get(url_for('user.delete_user', user_id=user.id))
         user = self._get_user_by_login(NEW_GROUP_LOGIN)
         self.assertIsNone(user)

   def test_admin(self):
      self._create_admin()

      with self.app.test_request_context():
         page = self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)

         # users_list.GET
         page = self.client.get(url_for('user.users_list'), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         # create_user.GET
         page = self.client.get(url_for('user.create_user'), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         # create_user.POST | user with role "ADMIN"
         NEW_ADMIN_LOGIN = self._generate_login()
         page = self.client.post(url_for('user.create_user'), data=dict(
               login=NEW_ADMIN_LOGIN,
               password=self.COMMON_PASSWORD,
               role=User_role.ADMIN,
               chat_id=None,
               status=User_status.INACTIVE
         ), follow_redirects=True)

         user = self._get_user_by_login(NEW_ADMIN_LOGIN)
         self.assertIsNotNone(user)

         # edit_user.GET
         page = self.client.get(url_for('user.edit_user', user_id=user.id), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         # delete_user.GET
         self.client.get(url_for('user.delete_user', user_id=user.id))
         user = self._get_user_by_login(NEW_ADMIN_LOGIN)
         self.assertIsNone(user)

         # create_user.POST | user with role "USER"
         NEW_USER_LOGIN = self._generate_login()
         page = self.client.post(url_for('user.create_user'), data=dict(
               login=NEW_USER_LOGIN,
               password=self.COMMON_PASSWORD,
               role=User_role.ADMIN,
               chat_id=None,
               status=User_status.INACTIVE
         ), follow_redirects=True)

         user = self._get_user_by_login(NEW_USER_LOGIN)
         self.assertIsNotNone(user)

         # edit_user.GET
         page = self.client.get(url_for('user.edit_user', user_id=user.id), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         # edit_user.POST
         EDIT_ROLE     = User_role.USER
         EDIT_STATUS   = User_status.ACTIVE
         EDIT_CHAT_ID  = -99
         EDIT_PASSWORD = 'EDIT_PASSWORD'

         page = self.client.post(url_for('user.edit_user', user_id=user.id), data=dict(
               login=NEW_USER_LOGIN,
               password=EDIT_PASSWORD,
               role=EDIT_ROLE,
               chat_id=EDIT_CHAT_ID,
               status=EDIT_STATUS,
               user_id=user.id
         ), follow_redirects=True)

         user = self._get_user_by_login(NEW_USER_LOGIN)
         self.assertIsNotNone(user)
         self.assertEqual(EDIT_ROLE, user.role)
         self.assertEqual(EDIT_STATUS, user.status)
         self.assertEqual(EDIT_CHAT_ID, user.telegram_id)

         # check new password
         self._login(NEW_USER_LOGIN, EDIT_PASSWORD)

         page = self.client.get(url_for('frontend.index'), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)

         # reset_password_user.GET
         page = self.client.get(url_for('user.reset_password_user', user_id=user.id), follow_redirects=False)

         user = self._get_user_by_login(NEW_USER_LOGIN)
         self.assertEqual(user.status, User_status.RESET)
         self.assertIsNotNone(user.reset_code)

         self._logout()

         # change_password_user.GET
         page = self.client.get(url_for('user.change_password_user', user_id=user.id, reset_code=user.reset_code), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         # change_password_user.POST
         NEW_PASSWORD = 'NEW_PASSWORD'
         page = self.client.post(url_for('user.change_password_user', user_id=user.id, reset_code=user.reset_code), data=dict(
               login=NEW_USER_LOGIN,
               password=NEW_PASSWORD,
               confirm=NEW_PASSWORD
         ), follow_redirects=True)

         # check new password
         self._login(NEW_USER_LOGIN, NEW_PASSWORD)

         page = self.client.get(url_for('frontend.index'), follow_redirects=False)
         self.assertEqual(page.status_code, 200)

         self._login(self.ADMIN_LOGIN, self.ADMIN_PASSWORD)

         # delete_user.GET
         self.client.get(url_for('user.delete_user', user_id=user.id))
         user = self._get_user_by_login(NEW_USER_LOGIN)
         self.assertIsNone(user)

   def test_user(self):
      self._create_user()

      with self.app.test_request_context():
         page = self._login(self.USER_LOGIN, self.USER_PASSWORD)

         # users_list.GET
         page = self.client.get(url_for('user.users_list'), follow_redirects=False)
         self.assertEqual(page.status_code, 302)

         # create_user.GET
         page = self.client.get(url_for('user.create_user'), follow_redirects=False)
         self.assertEqual(page.status_code, 302)

         # create_user.POST | user with role "USER"
         NEW_USER_LOGIN = self._generate_login()
         page = self.client.post(url_for('user.create_user'), data=dict(
               login=NEW_USER_LOGIN,
               password=self.COMMON_PASSWORD,
               role=User_role.USER,
               chat_id=None,
               status=User_status.ACTIVE
         ), follow_redirects=True)

         user = self._get_user_by_login(NEW_USER_LOGIN)
         self.assertIsNone(user)

   def test_group(self):
      self._create_group()

      with self.app.test_request_context():
         page = self._login(self.GROUP_LOGIN, self.GROUP_PASSWORD)

         # users_list.GET
         page = self.client.get(url_for('user.users_list'), follow_redirects=False)
         self.assertEqual(page.status_code, 302)

         # create_user.GET
         page = self.client.get(url_for('user.create_user'), follow_redirects=False)
         self.assertEqual(page.status_code, 302)

         # create_user.POST | user with role "GROUP"
         NEW_GROUP_LOGIN = self._generate_login()
         page = self.client.post(url_for('user.create_user'), data=dict(
               login=NEW_GROUP_LOGIN,
               password=self.COMMON_PASSWORD,
               role=User_role.GROUP,
               chat_id=None,
               status=User_status.ACTIVE
         ), follow_redirects=True)

         user = self._get_user_by_login(NEW_GROUP_LOGIN)
         self.assertIsNone(user)
