from tests.base_test_case import BaseTestCase


class TestConfig(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls._init_app()
        cls._print_test_desc(__name__)

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
