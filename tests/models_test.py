from aecore.test_utils import BaseTestCase
from aecore.models import UserProfile
from aeauth.models import ProviderUserProfile
from google.appengine.ext import ndb

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'

class GoogleUserProfile(ProviderUserProfile):

    provider = 'google'
    provider_url = 'google.com'
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
    token_url = 'https://accounts.google.com/o/oauth2/token'

    def test_method_call(self):
        return 'it worked.'

class TestProviderUserProfile(BaseTestCase):
    def setUp(self):
        super(TestProviderUserProfile, self).setUp()
        self.register_model('ProviderUserProfile', ProviderUserProfile)
        self.register_model('UserProfile', UserProfile)

    def test_get_callback_url(self):
        provider = 'google'
        domain = 'localhost:8080'
        callback_url = ProviderUserProfile.get_callback_url(domain, provider)
        self.assertEqual(callback_url, 'localhost:8080/auth/google/callback')

    def test_get_config(self):
        p = GoogleUserProfile()
        self.assertEqual(p.config.user_profile_model, 'aeauth.strategies.google.GoogleUserProfile')

    def test_Options(self):
        p = GoogleUserProfile()
        self.assertEqual(p.provider, 'google')
        self.assertEqual(p.provider_url, 'google.com')
        self.assertEqual(p.authorize_url, 'https://accounts.google.com/o/oauth2/auth')
        self.assertEqual(p.token_url, 'https://accounts.google.com/o/oauth2/token')

    def test_provider_property(self):
        p = GoogleUserProfile()
        self.assertEqual(p.provider, 'google')
        p.put()
        self.assertEqual(p.provider, 'google')

    def test_provider_query(self):
        p = GoogleUserProfile()
        qry = GoogleUserProfile.query().fetch()
        self.assertEqual(len(qry), 0)
        p.put()
        # query UserProfile
        qry = UserProfile.query().fetch()
        self.assertEqual(len(qry), 1)
        qry = GoogleUserProfile.query().fetch()
        self.assertEqual(len(qry), 1)

    def test_method_call_on_subclass(self):
        p = GoogleUserProfile()
        p.put()
        pq = UserProfile.query().get()
        v = pq.test_method_call()
        self.assertEqual(v, 'it worked.')

