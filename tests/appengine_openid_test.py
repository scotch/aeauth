from aeauth.main import application
from aecore.middleware import Request
from aecore.test_utils import BaseTestCase
from aecore.models import Config
from aecore.models import User
from aecore.models import UserProfile


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class TestAppEngineOpenIDStrategy(BaseTestCase):

    def setUp(self):
        super(TestAppEngineOpenIDStrategy, self).setUp()
        self.register_model('Config', Config)
        self.register_model('User', User)
        self.register_model('UserProfile', UserProfile)

    def test_handle_request(self):
        # No User or Profile
        p_count0 = UserProfile.query().count()
        u_count0 = User.query().count()
        self.assertEqual(p_count0, 0)
        self.assertEqual(u_count0, 0)
        # Create New User
        provider = 'gmail.com'
        req = Request.blank('/auth/appengine_openid?provider=' + provider)
        resp = req.get_response(application)
        self.assertEqual(resp.location, 'https://www.google.com/accounts/'
                                        'Login?continue=http%3A//localhost/'
                                        'auth/appengine_openid/callback')


