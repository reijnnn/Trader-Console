from tests.base_test_case import BaseTestCase
from flask                import url_for

class TestConfig(BaseTestCase):
   @classmethod
   def setUpClass(self):
      self._init_app(self)
      self._print_test_desc(self, __name__)

   def setUp(self):
      pass

   def tearDown(self):
      pass

   def test_config(self):
      self.assertEqual(self.app.config['ENV'], 'TST')

      self.assertTrue(self.app.config['TESTING'])

      self.assertFalse(self.app.config['WTF_CSRF_ENABLED'])
      self.assertFalse(self.app.config['DEBUG'])

      self.assertEqual(self.app.config['SERVER_NAME'], self.app.config['HOST'])
      self.assertEqual(self.app.config['SERVER_PORT'], self.app.config['PORT'])
