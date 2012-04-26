"""
    aeauth.profiles.password
    =============================

    :copyright: (c) 2011 Kyle Finley.
    :license: Apache Software License, see LICENSE for details.

"""
from __future__ import absolute_import
from aeauth.models import ProviderUserProfile
from aecore import types
from aecore.utils import flat_dict_to_nested_dict
import datetime
from webapp2_extras import security


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class PasswordUserProfile(ProviderUserProfile):

    provider = u'password'

    def get_profile_uid(self, **kwargs):
        return self.person.id

    def set_person(self):
        person = types.Person()
        raw = self.person_raw

        if not raw:
            raise AttributeError(message=u'person_raw not populated.')

        ## Required ##
        person.provider             = self.provider # u'facebook'
        person.id                   = raw.get('email') # u'12345'
        person.name                 = raw.get('name') # u'Mr. Joseph Robert Smarr, Esq'

        ### Accounts ###
        # You are required to create an account object for the providers
        # account. You may optionally add additional account, too.
        account                     = types.Account()
        account.name                = raw.get('name') # u'facebook'
        account.url                 = raw.get('url') # u'facebook.com'
        account.username            = raw.get('email') # u'123456789'
        person.accounts             = [account]

        ## Optional ##

        ### Name Details ###
        if raw.get('name'):
            person.givenName          = raw.get('givenName') # u'Joseph'
            person.additionalName     = raw.get('additionalName') # u'Robert'
            person.familyName         = raw.get('familyName') # u'Smarr'
            person.honorificPrefix    = raw.get('honorificPrefix') # u'Mr.'
            person.honorificSuffix    = raw.get('honorificSuffix') # u'Esq.'

        ### Singular Fields ###
        person.url                  = raw.get('url') # u'http://facebook.com/username'
        person.birthDate            = raw.get('birthDate') # datetime.datetime(1969, 7, 20, 1, 12, 3, 723097)
        person.description          = raw.get('description') # u'Longer description'
        person.email                = raw.get('email') # u'test@example.com'
        person.image                = raw.get('image')# u'http://awesome.jpg.to/'
        person.gender               = raw.get('gender') # u'male'
        person.location             = raw.get('location') # etype.Location(name=u'Springfield, VT')
        person.relationshipStatus   = raw.get('relationshipStatus') # u'single'
        person.locale               = raw.get('locale')

        if raw.get('affiliations'):
            for a in raw.get('affiliations'):
                affiliation                 = types.Affiliation()
                affiliation.name            = a.get('name') # u'BFA'
                affiliation.department      = a.get('department') # u'Graphic Design'
                affiliation.description     = a.get('description') # u'BFA Emphasis in Graphic Design'
                if a.get('startDate'):
                    affiliation.startDate   = datetime.datetime.strptime(a.get('startDate'), "%Y-%m-%dT%H:%M:%S") # datetime.datetime(2010, 1, 14, 10, 12, 3, 723097)
                if a.get('endDate'):
                    affiliation.endDate     = datetime.datetime.strptime(a.get('endDate'), "%Y-%m-%dT%H:%M:%S") # datetime.datetime(2012, 1, 14, 10, 12, 3, 723097)
                affiliation.location        = types.Place(name=a.get('location')) # types.Place(name=u'Kansas USA')

                org = a.get('organization')
                if org:
                    organization                = types.Organization()
                    organization.name           = org.get('name') # u'FHSU'
                    organization.description    = org.get('description')  # u'tiger'
                    affiliation.organization = organization
                person.affiliations.append(affiliation)

        self.person = person

    @staticmethod
    def _generate_password_hash( password):
        return security.generate_password_hash(password, length=12)

    @staticmethod
    def _check_password_hash(password_raw, password_hash):
        return security.check_password_hash(password_raw, password_hash)

    def _check_password(self, password):
        return self._check_password_hash(
            password, self.credentials['password'])
    check_password = _check_password

    def set_password(self, password):
        self.credentials = dict(password=self._generate_password_hash(password))

    @classmethod
    def handle_request(cls, request):
        post_dict = flat_dict_to_nested_dict(request.POST)
        # confirm that required fields are provided.
        # We pop the password, because we don't want to send it to
        # ``get_person()``
        password = post_dict.pop('password')
        email = post_dict.get('email')
        if not email or not password:
            raise Exception(u'Please provide a valid email '
                                  u'and a password.')
        obj = cls.get_key(cls.provider, email).get()
        if obj is None:
            obj = cls()
            obj.set_password(password)
        else:
            if not obj._check_password(password):
                raise Exception(u'The password that you\'ve provided '
                                      u'doesn\'t match our records. '
                                      u'Please try again.')
        obj.person_raw = post_dict
        obj.set_person()
        obj.set_key()
        obj.put()
        return None, obj
