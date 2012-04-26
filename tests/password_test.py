from aeauth.main import application
from aeauth.models import UserProfile
from aecore.models import User
from aecore.models import Config
from aecore.middleware import AECoreMiddleware
from aecore.middleware import Request
from aecore.test_utils import BaseTestCase


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'

application = AECoreMiddleware(application)

class TestPasswordHandler(BaseTestCase):

    def setUp(self):
        super(TestPasswordHandler, self).setUp()
        self.register_model('Config', Config)
        self.register_model('User', User)
        self.register_model('UserProfile', UserProfile)

    def test_post(self):
        email = 'test@example.com'
        password = 'password1'
        # No User
        u_count0 = User.query().count()
        self.assertEqual(u_count0, 0)
        # Create New User
        req = Request.blank('/auth/password',
            POST={
                'password': password,
                'email': email,
                'name': 'Kyle Finley',
                'givenName': 'Kyle',
                'additionalName': '"Danger"',
                'familyName': 'Finley',
                'gender': 'male',
                'affiliations-1.name': 'Aff 1 name',
                'affiliations-1.department': 'Aff 1 department',
                'affiliations-1.description': 'Aff 1 description',
                'affiliations-1.location': 'Aff 1 location',
                'affiliations-2.name': 'Aff 2 name',
                'affiliations-2.department': 'Aff 2 department',
                'affiliations-2.description': 'Aff 2 description',
                'affiliations-2.location': 'Aff 2 location',
                })

        req._load_session()
        resp = req.get_response(application)
        # Retrieve user from datastore
        user = User.query().get()
        p = user.data
        self.assertEqual(p.name, 'Kyle Finley')
        self.assertEqual(p.givenName, 'Kyle')
        self.assertEqual(p.additionalName, '"Danger"')
        self.assertEqual(p.familyName, 'Finley')
        self.assertEqual(p.gender, 'male')
        self.assertEqual(p.affiliations[0].name, 'Aff 1 name')
        self.assertEqual(p.affiliations[0].department, 'Aff 1 department')
        self.assertEqual(p.affiliations[0].description, 'Aff 1 description')
        self.assertEqual(p.affiliations[0].location.name, 'Aff 1 location')
        self.assertEqual(p.affiliations[1].name, 'Aff 2 name')
        self.assertEqual(p.affiliations[1].department, 'Aff 2 department')
        self.assertEqual(p.affiliations[1].description, 'Aff 2 description')
        self.assertEqual(p.affiliations[1].location.name, 'Aff 2 location')

        u_count1 = User.query().count()
        self.assertEqual(p_count1, 1)
        self.assertEqual(u_count1, 1)
        # Login User
        req = Request.blank('/auth/password',
            POST={'password': password, 'email': email})
        resp = req.get_response(application)
        # Make sure a new User is not created.
        p_count2 = UserProfile.query().count()
        u_count2 = User.query().count()
        self.assertEqual(p_count2, 1)
        self.assertEqual(u_count2, 1)
        # Wrong password
        req = Request.blank('/auth/password',
            POST={'password': 'fakepass', 'email': email})
        resp = req.get_response(application)

